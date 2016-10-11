export default store => next => action => (
  new Promise(
    () => store || next || action
  )
);
