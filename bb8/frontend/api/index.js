import auth from './auth'
import bot from './bot'

const apiClient = {
  ...auth,
  ...bot,
}

export default apiClient
