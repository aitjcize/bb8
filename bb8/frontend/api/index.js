import auth from './auth'
import bot from './bot'
import platforms from './platforms'

const apiClient = {
  ...auth,
  ...bot,
  ...platforms,
}

export default apiClient
