"use client";

import { HTMLAttributes, forwardRef } from 'react';
import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-react';

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'danger';
  title?: string;
  onClose?: () => void;
  dismissible?: boolean;
}

export const Alert = forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      children,
      variant = 'info',
      title,
      onClose,
      dismissible = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const variants = {
      info: {
        container: 'bg-blue-50 border-blue-200 text-blue-950',
        icon: <Info className="h-5 w-5 text-blue-600" aria-hidden="true" />,
        titleColor: 'text-blue-950',
      },
      success: {
        container: 'bg-green-50 border-green-200 text-green-950',
        icon: <CheckCircle className="h-5 w-5 text-green-600" aria-hidden="true" />,
        titleColor: 'text-green-950',
      },
      warning: {
        container: 'bg-yellow-50 border-yellow-200 text-yellow-950',
        icon: <AlertTriangle className="h-5 w-5 text-yellow-600" aria-hidden="true" />,
        titleColor: 'text-yellow-950',
      },
      danger: {
        container: 'bg-red-50 border-red-200 text-red-950',
        icon: <AlertCircle className="h-5 w-5 text-red-600" aria-hidden="true" />,
        titleColor: 'text-red-950',
      },
    };

    const config = variants[variant];

    return (
      <div
        ref={ref}
        role="alert"
        aria-live="polite"
        className={`border rounded-lg p-4 ${config.container} ${className}`}
        {...props}
      >
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">{config.icon}</div>
          
          <div className="flex-1 min-w-0">
            {title && (
              <h4 className={`font-semibold mb-1 ${config.titleColor}`}>{title}</h4>
            )}
            <div className="text-sm">{children}</div>
          </div>
          
          {dismissible && onClose && (
            <button
              onClick={onClose}
              className="flex-shrink-0 text-current opacity-70 hover:opacity-100 transition-opacity"
              aria-label="Cerrar alerta"
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';

