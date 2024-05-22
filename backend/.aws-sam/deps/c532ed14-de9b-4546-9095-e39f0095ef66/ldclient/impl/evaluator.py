from ldclient.context import Context
from ldclient.evaluation import BigSegmentsStatus, EvaluationDetail
from ldclient.impl import operators
from ldclient.impl.events.types import EventFactory, EventInputEvaluation
from ldclient.impl.model import *

import hashlib
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

# For consistency with past logging behavior, we are pretending that the evaluation logic still lives in
# the ldclient.evaluation module.
log = logging.getLogger('ldclient.flag')

__LONG_SCALE__ = float(0xFFFFFFFFFFFFFFF)

__BUILTINS__ = ["key", "secondary", "ip", "country", "email",
                "firstName", "lastName", "avatar", "name", "anonymous"]


# EvalResult is used internally to hold the EvaluationDetail result of an evaluation along with
# other side effects that are not exposed to the application, such as events generated by
# prerequisite evaluations, and the cached state of any Big Segments query that we may have
# ended up having to do for the context.
class EvalResult:
    __slots__ = ['detail', 'events', 'big_segments_status', 'big_segments_membership',
        'original_flag_key', 'prereq_stack', 'segment_stack']

    def __init__(self):
        self.detail = None
        self.events = None  # type: Optional[List[EventInputEvaluation]]
        self.big_segments_status = None  # type: Optional[str]
        self.big_segments_membership = None  # type: Optional[Dict[str, Optional[dict]]]
        self.original_flag_key = None  # type: Optional[str]
        self.prereq_stack = None  # type: Optional[List[str]]
        self.segment_stack = None  # type: Optional[List[str]]

    def add_event(self, event: EventInputEvaluation):
        if self.events is None:
            self.events = []
        self.events.append(event)

    def __repr__(self) -> str:  # used only in test debugging
        return "EvalResult(detail=%s, events=%s)" % (self.detail, self.events)


class EvaluationException(Exception):
    def __init__(self, message: str, error_kind: str = 'MALFORMED_FLAG'):
        self._message = message
        self._error_kind = error_kind
    
    @property
    def message(self) -> str:
        return self._message

    @property
    def error_kind(self) -> str:
        return self._error_kind


class Evaluator:
    """
    Encapsulates the feature flag evaluation logic. The Evaluator has no knowledge of the rest of the SDK environment;
    if it needs to retrieve flags or segments that are referenced by a flag, it does so through a read-only interface
    that is provided in the constructor. It also produces feature events as appropriate for any referenced prerequisite
    flags, but does not send them.
    """
    def __init__(
        self,
        get_flag: Callable[[str], Optional[FeatureFlag]],
        get_segment: Callable[[str], Optional[Segment]],
        get_big_segments_membership: Callable[[str], Tuple[Optional[dict], str]],
        logger: Optional[logging.Logger] = None
    ):
        """
        :param get_flag: function provided by LDClient that takes a flag key and returns either the flag or None
        :param get_segment: same as get_flag but for segments
        :param get_big_segments_membership: takes a context key (not a context hash) and returns a tuple of
            (membership, status) where membership is as defined in BigSegmentStore, and status is one
            of the BigSegmentStoreStatus constants
        """
        self.__get_flag = get_flag
        self.__get_segment = get_segment
        self.__get_big_segments_membership = get_big_segments_membership
        self.__logger = logger

    def evaluate(self, flag: FeatureFlag, context: Context, event_factory: EventFactory) -> EvalResult:
        state = EvalResult()
        state.original_flag_key = flag.key
        try:
            state.detail = self._evaluate(flag, context, state, event_factory)
        except EvaluationException as e:
            if self.__logger is not None:
                self.__logger.error('Could not evaluate flag "%s": %s' % (flag.key, e.message))
            state.detail = EvaluationDetail(None, None, {'kind': 'ERROR', 'errorKind': e.error_kind})
            return state
        if state.big_segments_status is not None:
            state.detail.reason['bigSegmentsStatus'] = state.big_segments_status
        return state

    def _evaluate(self, flag: FeatureFlag, context: Context, state: EvalResult, event_factory: EventFactory) -> EvaluationDetail:
        if not flag.on:
            return _get_off_value(flag, {'kind': 'OFF'})

        prereq_failure_reason = self._check_prerequisites(flag, context, state, event_factory)
        if prereq_failure_reason is not None:
            return _get_off_value(flag, prereq_failure_reason)

        # Check to see if any context targets match:
        target_result = self._check_targets(flag, context)
        if target_result is not None:
            return target_result

        # Now walk through the rules to see if any match
        for index, rule in enumerate(flag.rules):
            if self._rule_matches_context(rule, context, state):
                return _get_value_for_variation_or_rollout(flag, rule.variation_or_rollout, context,
                    {'kind': 'RULE_MATCH', 'ruleIndex': index, 'ruleId': rule.id})

        # Walk through fallthrough and see if it matches
        return _get_value_for_variation_or_rollout(flag, flag.fallthrough, context, {'kind': 'FALLTHROUGH'})

    def _check_prerequisites(self, flag: FeatureFlag, context: Context, state: EvalResult, event_factory: EventFactory) -> Optional[dict]:
        failed_prereq = None
        prereq_res = None
        if flag.prerequisites.count == 0:
            return None
        
        try:
            # We use the state object to guard against circular references in prerequisites. To avoid
            # the overhead of creating the state.prereq_stack list in the most common case where
            # there's only a single level prerequisites, we treat state.original_flag_key as the first
            # element in the stack.
            flag_key = flag.key
            if flag_key != state.original_flag_key:
                if state.prereq_stack is None:
                    state.prereq_stack = []
                state.prereq_stack.append(flag_key)
            
            for prereq in flag.prerequisites:
                prereq_key = prereq.key
                if (prereq_key == state.original_flag_key or
                    (state.prereq_stack is not None and prereq.key in state.prereq_stack)):
                    raise EvaluationException(('prerequisite relationship to "%s" caused a circular reference;' +
                        ' this is probably a temporary condition due to an incomplete update') % prereq_key)

                prereq_flag = self.__get_flag(prereq_key)
                if prereq_flag is None:
                    log.warning("Missing prereq flag: " + prereq_key)
                    failed_prereq = prereq
                else:
                    prereq_res = self._evaluate(prereq_flag, context, state, event_factory)
                    # Note that if the prerequisite flag is off, we don't consider it a match no matter what its
                    # off variation was. But we still need to evaluate it in order to generate an event.
                    if (not prereq_flag.on) or prereq_res.variation_index != prereq.variation:
                        failed_prereq = prereq
                    event = event_factory.new_eval_event(prereq_flag, context, prereq_res, None, flag)
                    state.add_event(event)
                if failed_prereq:
                    return {'kind': 'PREREQUISITE_FAILED', 'prerequisiteKey': failed_prereq.key}
            return None
        finally:
            if state.prereq_stack is not None and len(state.prereq_stack) != 0:
                state.prereq_stack.pop()

    def _check_targets(self, flag: FeatureFlag, context: Context) -> Optional[EvaluationDetail]:
        user_targets = flag.targets
        context_targets = flag.context_targets
        if len(context_targets) == 0:
            # old-style data has only targets for users
            if len(user_targets) != 0:
                user_context = context.get_individual_context(Context.DEFAULT_KIND)
                if (user_context is None):
                    return None
                key = user_context.key
                for t in user_targets:
                    if key in t.values:
                        return _target_match_result(flag, t.variation)
            return None
        for t in context_targets:
            kind = t.context_kind or Context.DEFAULT_KIND
            var = t.variation
            actual_context = context.get_individual_context(kind)
            if actual_context is None:
                continue
            key = actual_context.key
            if kind == Context.DEFAULT_KIND:
                for ut in user_targets:
                    if ut.variation == var:
                        if key in ut.values:
                            return _target_match_result(flag, var)
                        break
                continue
            if key in t.values:
                return _target_match_result(flag, var)
        return None

    def _rule_matches_context(self, rule: FlagRule, context: Context, state: EvalResult) -> bool:
        for clause in rule.clauses:
            if not self._clause_matches_context(clause, context, state):
                return False
        return True

    def _clause_matches_context(self, clause: Clause, context: Context, state: EvalResult) -> bool:
        if clause.op == 'segmentMatch':
            for seg_key in clause.values:
                segment = self.__get_segment(seg_key)
                if segment is not None and self._segment_matches_context(segment, context, state):
                    return _maybe_negate(clause, True)
            return _maybe_negate(clause, False)
        
        attr = clause.attribute
        if attr is None:
            return False
        if attr.depth == 1 and attr[0] == 'kind':
            return _maybe_negate(clause, _match_clause_by_kind(clause, context))
        actual_context = context.get_individual_context(clause.context_kind or Context.DEFAULT_KIND)
        if actual_context is None:
            return False
        context_value = _get_context_value_by_attr_ref(actual_context, attr)
        if context_value is None:
            return False
        
        # is the attr an array?
        if isinstance(context_value, (list, tuple)):
            for v in context_value:
                if _match_single_context_value(clause, v):
                    return _maybe_negate(clause, True)
            return _maybe_negate(clause, False)
        return _maybe_negate(clause, _match_single_context_value(clause, context_value))

    def _segment_matches_context(self, segment: Segment, context: Context, state: EvalResult) -> bool:
        if state.segment_stack is not None and segment.key in state.segment_stack:
            raise EvaluationException(('segment rule referencing segment "%s" caused a circular reference;' +
                ' this is probably a temporary condition due to an incomplete update') % segment.key)
        if segment.unbounded:
            return self._big_segment_match_context(segment, context, state)
        return self._simple_segment_match_context(segment, context, state, True)

    def _simple_segment_match_context(self, segment: Segment, context: Context, state: EvalResult, use_includes_and_excludes: bool) -> bool:
        if use_includes_and_excludes:
            if _context_key_is_in_target_list(context, None, segment.included):
                return True
            for t in segment.included_contexts:
                if _context_key_is_in_target_list(context, t.context_kind, t.values):
                    return True
            if _context_key_is_in_target_list(context, None, segment.excluded):
                return False
            for t in segment.excluded_contexts:
                if _context_key_is_in_target_list(context, t.context_kind, t.values):
                    return False
        if segment.rules.count != 0:
            # Evaluating rules means we might be doing recursive segment matches, so we'll push the current
            # segment key onto the stack for cycle detection.
            if state.segment_stack is None:
                state.segment_stack = []
            state.segment_stack.append(segment.key)
            try:
                for rule in segment.rules:
                    if self._segment_rule_matches_context(rule, context, state, segment.key, segment.salt):
                        return True
                return False
            finally:
                state.segment_stack.pop()
        return False

    def _segment_rule_matches_context(self, rule: SegmentRule, context: Context, state: EvalResult, segment_key: str, salt: str) -> bool:
        for clause in rule.clauses:
            if not self._clause_matches_context(clause, context, state):
                return False

        # If the weight is absent, this rule matches
        if rule.weight is None:
            return True

        # All of the clauses are met. See if the context buckets in
        bucket = _bucket_context(None, context, rule.rollout_context_kind, segment_key, salt, rule.bucket_by)
        weight = rule.weight / 100000.0
        return bucket < weight

    def _big_segment_match_context(self, segment: Segment, context: Context, state: EvalResult) -> bool:
        generation = segment.generation
        if generation is None:
            # Big segment queries can only be done if the generation is known. If it's unset,
            # that probably means the data store was populated by an older SDK that doesn't know
            # about the generation property and therefore dropped it from the JSON data. We'll treat
            # that as a "not configured" condition.
            state.big_segments_status = BigSegmentsStatus.NOT_CONFIGURED
            return False
        
        # A big segment can only apply to one context kind, so if we don't have a key for that kind,
        # we don't need to bother querying the data.
        match_context = context.get_individual_context(segment.unbounded_context_kind or Context.DEFAULT_KIND)
        if match_context is None:
            return False
        key = match_context.key

        membership = None
        has_cached_membership = False
        if state.big_segments_membership is not None:
            if key in state.big_segments_membership:
                has_cached_membership = True
                membership = state.big_segments_membership[key]
                # Note that we could have cached a None result from a query, in which case membership
                # will be None but has_cached_membership will be True.
        if not has_cached_membership:
            if self.__get_big_segments_membership is None:
                state.big_segments_status = BigSegmentsStatus.NOT_CONFIGURED
                return False
            result = self.__get_big_segments_membership(key)
            # Note that this query is just by key; the context kind doesn't matter because any given
            # Big Segment can only reference one context kind. So if segment A for the "user" kind
            # includes a "user" context with key X, and segment B for the "org" kind includes an "org"
            # context with the same key X, it is fine to say that the membership for key X is
            # segment A and segment B-- there is no ambiguity.
            membership, state.big_segments_status = result
            if state.big_segments_membership is None:
                state.big_segments_membership = {}
            state.big_segments_membership[key] = membership
        included = None if membership is None else membership.get(_make_big_segment_ref(segment), None)
        if included is not None:
            return included
        return self._simple_segment_match_context(segment, context, state, False)


# The following functions are declared outside Evaluator because they do not depend on any
# of Evaluator's state.

def _get_variation(flag: FeatureFlag, variation: int, reason: dict) -> EvaluationDetail:
    vars = flag.variations
    if variation < 0 or variation >= len(vars):
        return EvaluationDetail(None, None, error_reason('MALFORMED_FLAG'))
    return EvaluationDetail(vars[variation], variation, reason)

def _get_off_value(flag: FeatureFlag, reason: dict) -> EvaluationDetail:
    off_var = flag.off_variation
    if off_var is None:
        return EvaluationDetail(None, None, reason)
    return _get_variation(flag, off_var, reason)

def _get_value_for_variation_or_rollout(flag: FeatureFlag, vr: VariationOrRollout, context: Context, reason: dict) -> EvaluationDetail:
    index, inExperiment = _variation_index_for_context(flag, vr, context)
    if index is None:
        return EvaluationDetail(None, None, error_reason('MALFORMED_FLAG'))
    if inExperiment:
        reason['inExperiment'] = inExperiment
    return _get_variation(flag, index, reason)

def _variation_index_for_context(flag: FeatureFlag, vr: VariationOrRollout, context: Context) -> Tuple[Optional[int], bool]:
    var = vr.variation
    if var is not None:
        return (var, False)

    rollout = vr.rollout
    if rollout is None:
        return (None, False)
    variations = rollout.variations
    if len(variations) == 0:
        return (None, False)
    
    bucket_by = None if rollout.is_experiment else rollout.bucket_by
    bucket = _bucket_context(
        rollout.seed,
        context,
        rollout.context_kind,
        flag.key,
        flag.salt,
        bucket_by
        )
    is_experiment = rollout.is_experiment and bucket >= 0
    # _bucket_context returns a negative value if the context didn't exist, in which case we
    # still end up returning the first bucket, but we will force the "in experiment" state to be false.

    sum = 0.0
    for wv in variations:
        sum += wv.weight / 100000.0
        if bucket < sum:
            is_experiment_partition = is_experiment and not wv.untracked
            return (wv.variation, is_experiment_partition)

    # The context's bucket value was greater than or equal to the end of the last bucket. This could happen due
    # to a rounding error, or due to the fact that we are scaling to 100000 rather than 99999, or the flag
    # data could contain buckets that don't actually add up to 100000. Rather than returning an error in
    # this case (or changing the scaling, which would potentially change the results for *all* contexts), we
    # will simply put the context in the last bucket.
    is_experiment_partition = is_experiment and not variations[-1].untracked
    return (variations[-1].variation, is_experiment_partition)

def _bucket_context(
    seed: Optional[int],
    context: Context,
    context_kind: Optional[str],
    key: str,
    salt: str,
    bucket_by: Optional[AttributeRef]
    ) -> float:
    match_context = context.get_individual_context(context_kind or Context.DEFAULT_KIND)
    if match_context is None:
        return -1
    clause_value = match_context.key if bucket_by is None else _get_context_value_by_attr_ref(match_context, bucket_by)
    if clause_value is None:
        return 0.0
    bucket_by_value = _bucketable_string_value(clause_value)
    if bucket_by_value is None:
        return 0.0
    id_hash = clause_value
    if seed is not None:
        prefix = str(seed)
    else:
        prefix = '%s.%s' % (key, salt)
    hash_key = '%s.%s' % (prefix, id_hash)
    hash_val = int(hashlib.sha1(hash_key.encode('utf-8')).hexdigest()[:15], 16)
    result = hash_val / __LONG_SCALE__
    return result

def _bucketable_string_value(u_value) -> Optional[str]:
    if isinstance(u_value, bool):
        return None
    elif isinstance(u_value, (str, int)):
        return str(u_value)

    return None

def _context_key_is_in_target_list(context: Context, context_kind: Optional[str], keys: Set[str]) -> bool:
    if keys is None or len(keys) == 0:
        return False
    match_context = context.get_individual_context(context_kind or Context.DEFAULT_KIND)
    return match_context is not None and match_context.key in keys

def _get_context_value_by_attr_ref(context: Context, attr: AttributeRef) -> Any:
    if attr is None:
        raise EvaluationException("rule clause did not specify an attribute")
    if attr.error is not None:
        raise EvaluationException("invalid attribute reference: " + attr.error)
    name = attr[0]
    if name is None:
        return None
    value = context.get(name)
    depth = attr.depth
    i = 1
    while i < depth:
        if not isinstance(value, dict):
            return None  # can't get subproperty if we're not in a JSON object
        value = value.get(attr[i])
        i += 1
    return value

def _match_single_context_value(clause: Clause, context_value: Any) -> bool:
    op_fn = operators.ops.get(clause.op)
    if op_fn is None:
        return False
    values_preprocessed = clause.values_preprocessed
    for i, v in enumerate(clause.values):
        preprocessed = None if values_preprocessed is None else values_preprocessed[i]
        if op_fn(context_value, v, preprocessed):
            return True
    return False

def _match_clause_by_kind(clause: Clause, context: Context) -> bool:
    # If attribute is "kind", then we treat operator and values as a match expression against a list
    # of all individual kinds in the context. That is, for a multi-kind context with kinds of "org"
    # and "user", it is a match if either of those strings is a match with Operator and Values.
    for i in range(context.individual_context_count):
        c = context.get_individual_context(i)
        if c is not None and _match_single_context_value(clause, c.kind):
            return True
    return False

def _maybe_negate(clause: Clause, val: bool) -> bool:
    return not val if clause.negate else val

def _make_big_segment_ref(segment: Segment) -> str:
    # The format of Big Segment references is independent of what store implementation is being
    # used; the store implementation receives only this string and does not know the details of
    # the data model. The Relay Proxy will use the same format when writing to the store.
    return "%s.g%d" % (segment.key, segment.generation or 0)

def _target_match_result(flag: FeatureFlag, var: int) -> EvaluationDetail:
    return _get_variation(flag, var, {'kind': 'TARGET_MATCH'})

def error_reason(error_kind: str) -> dict:
    return {'kind': 'ERROR', 'errorKind': error_kind}