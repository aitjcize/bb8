import auth from './auth'
import bot from './bot'
import platforms from './platforms'
import broadcast from './broadcast'

const apiClient = {
  ...auth,
  ...bot,
  ...platforms,
  ...broadcast,
}

export default apiClient
