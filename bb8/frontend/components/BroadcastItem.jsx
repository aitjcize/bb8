import React from 'react'
import Moment from 'moment'
import FlatButton from 'material-ui/FlatButton'
import { Card, CardActions, CardHeader } from 'material-ui/Card'

const BroadcastItem = props => (
  <Card>
    <CardHeader
      title={props.broadcast.name}
      subtitle={props.broadcast.status}
    />
    <CardActions>
      <span>
        { Moment.unix(props.broadcast.scheduledTime).format('ll') }
      </span>
      <FlatButton
        onClick={props.handleEdit}
        label="Edit"
      />
      <FlatButton
        onClick={props.handleDelete}
        label="Delete"
      />
      <FlatButton
        onClick={props.handleSend}
        label="Send Now"
      />
    </CardActions>
  </Card>
)

BroadcastItem.propTypes = {
  handleEdit: React.PropTypes.func,
  handleDelete: React.PropTypes.func,
  handleSend: React.PropTypes.func,
  broadcast: React.PropTypes.shape({
    name: React.PropTypes.string,
    status: React.PropTypes.string,
    scheduledTime: React.PropTypes.number,
  }),
}

export default BroadcastItem
