import React from 'react';

interface PlaceholderWidgetProps {
  name: string;
}

export const PlaceholderWidget: React.FC<PlaceholderWidgetProps> = ({ name }) => {
  return (
    <div className="w-full h-full bg-neutral-200 flex items-center justify-center border border-neutral-400">
      <p className="text-neutral-600 font-mono text-lg">{name}</p>
    </div>
  );
};
