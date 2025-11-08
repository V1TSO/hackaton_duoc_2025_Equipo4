export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export interface FormValidators {
  [key: string]: (value: any, formData?: Record<string, any>) => ValidationResult;
}

export const validators = {
  required: (fieldName: string) => (value: any): ValidationResult => {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return { isValid: false, error: `${fieldName} es obligatorio` };
    }
    return { isValid: true };
  },

  email: (value: string): ValidationResult => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return { isValid: false, error: 'Ingresa un correo electrónico válido' };
    }
    return { isValid: true };
  },

  minLength: (min: number) => (value: string): ValidationResult => {
    if (value.length < min) {
      return { isValid: false, error: `Debe tener al menos ${min} caracteres` };
    }
    return { isValid: true };
  },

  maxLength: (max: number) => (value: string): ValidationResult => {
    if (value.length > max) {
      return { isValid: false, error: `No puede exceder ${max} caracteres` };
    }
    return { isValid: true };
  },

  minValue: (min: number) => (value: number): ValidationResult => {
    if (value < min) {
      return { isValid: false, error: `El valor mínimo es ${min}` };
    }
    return { isValid: true };
  },

  maxValue: (max: number) => (value: number): ValidationResult => {
    if (value > max) {
      return { isValid: false, error: `El valor máximo es ${max}` };
    }
    return { isValid: true };
  },

  passwordStrength: (value: string): ValidationResult => {
    if (value.length < 6) {
      return { isValid: false, error: 'La contraseña debe tener al menos 6 caracteres' };
    }
    
    const hasNumber = /\d/.test(value);
    const hasLetter = /[a-zA-Z]/.test(value);
    
    if (!hasNumber || !hasLetter) {
      return { isValid: false, error: 'La contraseña debe contener letras y números' };
    }
    
    return { isValid: true };
  },

  matchField: (fieldName: string, matchFieldName: string) => (
    value: string,
    formData?: Record<string, any>
  ): ValidationResult => {
    if (!formData || value !== formData[matchFieldName]) {
      return { isValid: false, error: `${fieldName} no coincide con ${matchFieldName}` };
    }
    return { isValid: true };
  },

  pattern: (regex: RegExp, errorMessage: string) => (value: string): ValidationResult => {
    if (!regex.test(value)) {
      return { isValid: false, error: errorMessage };
    }
    return { isValid: true };
  },
};

export function validateField(
  value: any,
  validatorFns: Array<(value: any, formData?: Record<string, any>) => ValidationResult>,
  formData?: Record<string, any>
): ValidationResult {
  for (const validator of validatorFns) {
    const result = validator(value, formData);
    if (!result.isValid) {
      return result;
    }
  }
  return { isValid: true };
}

export function validateForm(
  formData: Record<string, any>,
  validationRules: Record<string, Array<(value: any, formData?: Record<string, any>) => ValidationResult>>
): Record<string, string> {
  const errors: Record<string, string> = {};
  
  for (const [field, rules] of Object.entries(validationRules)) {
    const result = validateField(formData[field], rules, formData);
    if (!result.isValid && result.error) {
      errors[field] = result.error;
    }
  }
  
  return errors;
}

