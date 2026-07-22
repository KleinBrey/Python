import React from 'react';
import { LoaderCircle } from 'lucide-react';
import { cn } from '@/lib/utils.js';

function Spinner({ className, ...props }) {
  return (
    <LoaderCircle
      aria-label="加载中"
      role="status"
      className={cn('size-5 animate-spin', className)}
      {...props}
    />
  );
}

export { Spinner };
