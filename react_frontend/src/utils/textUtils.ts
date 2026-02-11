/**
 * Capitaliza la primera letra de una cadena de texto.
 * @param str La cadena de texto a capitalizar.
 * @returns La cadena con la primera letra en mayúscula.
 */
export const capitalizeFirstLetter = (str: string): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};
