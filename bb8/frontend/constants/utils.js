export function createRequestTypes(base) {
  return {
    REQUEST: `${base}_REQUEST`,
    SUCCESS: `${base}_SUCCESS`,
    ERROR: `${base}_ERROR`,
  }
}

export function createDialogTypes(base) {
  return {
    OPEN: `${base}_OPEN`,
    CONFIRM: `${base}_CONFIRM`,
    CANCEL: `${base}_CANCEL`,
  }
}
