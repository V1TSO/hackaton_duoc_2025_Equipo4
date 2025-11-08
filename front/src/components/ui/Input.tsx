"use client";

import { forwardRef, InputHTMLAttributes, useState } from 'react';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      type = 'text',
      id,
      className = '',
      containerClassName = '',
      disabled,
      required,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = `${inputId}-error`;
    const helperId = `${inputId}-helper`;
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;

    const describedBy = [
      error ? errorId : '',
      helperText ? helperId : '',
      ariaDescribedBy || '',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={`space-y-2 ${containerClassName}`}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-950"
          >
            {label}
            {required && <span className="text-red-600 ml-1" aria-label="obligatorio">*</span>}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true">
              {leftIcon}
            </div>
          )}
          
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            disabled={disabled}
            required={required}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={describedBy || undefined}
            className={`
              w-full px-4 py-2.5 
              ${leftIcon ? 'pl-10' : ''} 
              ${rightIcon || isPassword ? 'pr-10' : ''}
              rounded-lg border-0
              bg-gray-50 text-gray-950 text-sm
              placeholder:text-gray-500
              outline-none transition-all
              focus:bg-gray-100 focus:ring-0 focus:outline-none
              disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500
              min-h-[44px]
              shadow-none
              ${className}
            `}
            style={{ border: 'none', outline: 'none' }}
            {...props}
          />
          
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff size={18} aria-hidden="true" />
              ) : (
                <Eye size={18} aria-hidden="true" />
              )}
            </button>
          )}
          
          {!isPassword && rightIcon && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true">
              {rightIcon}
            </div>
          )}
        </div>
        
        {error && (
          <div id={errorId} className="flex items-start gap-1.5 text-sm text-red-600" role="alert">
            <AlertCircle size={16} className="flex-shrink-0 mt-0.5" aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}
        
        {helperText && !error && (
          <p id={helperId} className="text-xs text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

