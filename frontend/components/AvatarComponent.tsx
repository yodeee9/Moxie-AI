import React, { useEffect } from 'react';
import { Rive, useRive, Layout, Fit, Alignment } from 'rive-react';

const AvatarComponent: React.FC = () => {
  const { rive, RiveComponent } = useRive({
    src: '/office2.riv', // パスを確認
    stateMachines: 'State Machine 1', // 状態マシン名を正しく設定
    layout: new Layout({
      fit: Fit.Height,
      alignment: Alignment.Center,
    }),
    autoplay: true,
  });

  useEffect(() => {
    if (rive) {
      const stateMachineInputs = rive.stateMachineInputs('State Machine 1');
      if (stateMachineInputs) {
        const visemeInput = stateMachineInputs.find(input => input.name === 'main animation');
        const listeningInput = stateMachineInputs.find(input => input.name === 'main animation');
        const thinkingInput = stateMachineInputs.find(input => input.name === 'main animation');
        
        window.setVisemeNumber = (value) => {
          if (visemeInput) visemeInput.value = parseFloat(value);
        };

        window.setListening = (value) => {
          if (listeningInput) listeningInput.value = value;
        };

        window.setThinking = (value) => {
          if (thinkingInput) thinkingInput.value = value;
        };
      }
    }
  }, [rive]);

  return <RiveComponent className="rive-avatar" />;
};

export default AvatarComponent;
