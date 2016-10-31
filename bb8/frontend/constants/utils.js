function createRequestTypes(base) {
  return {
    REQUEST: `${base}_REQUEST`,
    SUCCESS: `${base}_SUCCESS`,
    ERROR: `${base}_ERROR`,
  }
}

export default createRequestTypes
