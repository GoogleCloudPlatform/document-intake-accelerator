/** This page is common throughout the as it contains the header section which consist of a title for the app
 */

import { Card } from 'react-bootstrap';
import { Row, Col, Image } from 'react-bootstrap';
import {
  Link
} from 'react-router-dom';
import '../css/Headers.css'
import imgFile from '../images/userlogo.png'
import gCloud from '../images/googleLogo.png'

function Headers() {

  const signout = () => {
    localStorage.clear();
  }

  return (
    <div className="haContainer">
      <Card className="cardName">
        <Card.Body>
          <Card.Text as='div' style={{ fontWeight: 'bolder' }}>
            {/* <Container> */}
            <Row>
              <Col className="col-10">
                <Link className="overviewLabel" to="/" >
                  <Image src={gCloud} width='70px' height='40px' />
                  <label style={{ fontSize: '18px', marginBottom: '10px', cursor: 'pointer' }}>Automated Document Processing</label>
                </Link>
              </Col>

              {/* <Col className="col-1"></Col> */}

              <Col className="col-1">
                <Image src={imgFile} className="userIcon" />
              </Col>
              <Col className="col-1">
                <div className="dropdown">
                  <label className="userName">
                    {localStorage.getItem('user').split('@')[0]}
                  </label>
                  <div className="item">
                    <Link to={{
                      pathname: '/login',
                    }} style={{ textDecoration: 'none', fontSize: '14px', fontWeight: 'normal' }} onClick={signout}>Signout</Link>
                  </div>
                </div>

              </Col>
            </Row>
            {/* </Container> */}




          </Card.Text>
        </Card.Body>
      </Card>
    </div>
  )
}

export default Headers;