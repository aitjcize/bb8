import EntitiesReducer from './EntitiesReducer'

const wrapEntities = (entities) => {
  return {
    payload: {
      entities,
    },
  }
}

describe('Reducer for entities', () => {
  it('should merge the entities', () => {
    expect(EntitiesReducer({
      foo: {
        1: {
          a: 2,
        },
      },
    }, wrapEntities({
      foo: {
        2: {
          b: 2,
        }
      }
    }))).toEqual({
      foo: {
        1: {
          a: 2,
        },
        2: {
          b: 2,
        },
      }
    })
  })

  it('should overwrite the old entities', () => {
    expect(EntitiesReducer({
      foo: {
        1: {
          a: 2,
        },
      },
    }, wrapEntities({
      foo: {
        1: {
          a: 3,
        }
      }
    }))).toEqual({
      foo: {
        1: {
          a: 3,
        },
      }
    })
  })

  it('should overwrite if new value is empty array', () => {
    expect(EntitiesReducer({
      foo: {
        1: {
          a: [1, 2, 3],
        },
      },
    }, wrapEntities({
      foo: {
        1: {
          a: [],
        }
      }
    }))).toEqual({
      foo: {
        1: {
          a: [],
        },
      }
    })
  })

  it('should merge the original value and new value', () => {
    expect(EntitiesReducer({
      foo: {
        1: {
          a: 1,
          b: 2,
        },
      },
    }, wrapEntities({
      foo: {
        1: {
          b: 3,
          c: 4,
        }
      }
    }))).toEqual({
      foo: {
        1: {
          a: 1,
          b: 3,
          c: 4,
        },
      }
    })
  })
})
