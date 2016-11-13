import getMuiTheme from 'material-ui/styles/getMuiTheme'
import {
  tealA400,
  tealA700,
  teal50,
  grey600,
} from 'material-ui/styles/colors'

export const ModifiedTheme = {
  palette: {
    primary1Color: tealA400,
    accent1Color: tealA700,
    accent2Color: teal50,
    textColor: grey600,
  },
  toolbar: {
    height: '4em',
    backgroundColor: tealA400,
  },
}

const Theme = getMuiTheme(ModifiedTheme)

export default Theme
