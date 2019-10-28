function applyFilter(query, filter = 'ga:eventCategory!=Parser') {
  return Object.assign(query, {
    filter,
  })
}

function applyTime(query, viewId, start, end) {
  return Object.assign(query, {
    ids: viewId,
    'start-date': start,
    'end-date': end,
  })
}

export const numUsersByPlatformQuery = (gaId, start, end) => applyFilter(applyTime({
  metrics: 'ga:users',
  dimensions: 'ga:eventCategory',
}, gaId, start, end))

export const numUsersByNewOrReturnQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:users',
  dimensions: 'ga:userType',
}, gaId, start, end)

export const numUsersQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:users',
}, gaId, start, end)

export const numUsersByDateQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:users',
  dimensions: 'ga:date',
}, gaId, start, end)

export const numNewUsersQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:newUsers',
}, gaId, start, end)

export const numNewUsersByDateQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:newUsers',
  dimensions: 'ga:date',
}, gaId, start, end)

export const sessionByDateQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:sessions',
  dimensions: 'ga:date',
}, gaId, start, end)

export const popularBlocksQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:pageviews',
  dimensions: 'ga:pagePath',
  sort: '-ga:pageviews',
  'max-results': 10,
}, gaId, start, end)

export const popularInputsQuery = (gaId, start, end) => applyTime({
  metrics: 'ga:totalEvents',
  dimensions: 'ga:eventLabel',
  sort: '-ga:totalEvents',
  'max-results': 10,
}, gaId, start, end)

