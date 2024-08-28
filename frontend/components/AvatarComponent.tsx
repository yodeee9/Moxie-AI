import React, { useEffect } from 'react';
import { useRive, Layout, Fit, Alignment, useStateMachineInput } from 'rive-react';

const AvatarComponent: React.FC = () => {
  const { rive, RiveComponent } = useRive({
    src: '/office4.riv', 
    stateMachines: 'State Machine 1', 
    layout: new Layout({
      fit: Fit.FitHeight,
      alignment: Alignment.Center,
    }),
    autoplay: true,
  });

  // `useStateMachineInput`を使用して、`levelInput`を取得
  const levelInput = useStateMachineInput(rive, 'State Machine 1', 'Number 1');

  useEffect(() => {
    if (rive && levelInput) {
      window.setChatHistory = () => {
        levelInput.value = 0;

        setTimeout(() => {
          levelInput.value = 6;
        }, 3000);
      };
    }
  }, [rive, levelInput]);

  return <RiveComponent className="rive-avatar" />;
};

export default AvatarComponent;
