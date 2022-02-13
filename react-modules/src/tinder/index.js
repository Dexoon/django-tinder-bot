import React, {useState} from "react";
import ReactDOM from "react-dom";
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image'
import 'bootstrap/dist/css/bootstrap.min.css';
import alert from "bootstrap/js/src/alert";
import Container from 'react-bootstrap/Container'
import Carousel from 'react-bootstrap/Carousel'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import 'bootstrap-icons/font/bootstrap-icons.css';

const UserHeader = ({username, first_name, last_name}) => <>
    {isNaN(username) && <a href={'https://t.me/' + username}>@{username}</a>}
    <h2>{first_name} {last_name}</h2>
</>

const set_like = (user_id, setLike, setMutual) => {
    fetch(`/like/${user_id}`)
        .then(res => res.json())
        .then(
            (result) => {
                console.log(result)
                setLike(true);
                if (result.mutual) {
                    setMutual(true)
                }
            },
            // Примечание: важно обрабатывать ошибки именно здесь, а не в блоке catch(),
            // чтобы не перехватывать исключения из ошибок в самих компонентах.
            (error) => {
                alert('ЧТо-то пошло не так')
            }
        )
}
const unlike = (user_id, setLike, setMutual) => {
    fetch(`/unlike/${user_id}`)
        .then(res => res.json())
        .then(
            (result) => {
                setLike(false);
                setMutual(false);
            },
            // Примечание: важно обрабатывать ошибки именно здесь, а не в блоке catch(),
            // чтобы не перехватывать исключения из ошибок в самих компонентах.
            (error) => {
                alert('ЧТо-то пошло не так')
            }
        )
}

const PhotoCarousel = ({photos}) =>
    <Carousel variant="dark" interval={null} indicators={false}>
        {photos.map((photo) =>
            <Carousel.Item>
                <Image style={{display: 'block', margin: 'auto', height: '100px'}}
                       key={photo[0]} roundedCircle src={'/' + photo[0]}/>
            </Carousel.Item>)}
    </Carousel>


const Line = ({user_id, username, first_name, last_name, photos, initial_like, initial_mutual}) => {
    const [like, setLike] = useState(initial_like);
    const [mutual, setMutual] = useState(initial_mutual);
    let icon = 'heart';
    let onclick = set_like;
    if (like) {
        icon = 'heart-fill';
        onclick = unlike;
        if (mutual) {
            icon = 'arrow-through-heart-fill'
        }
    }
    return <Row>
        <Col>
            <Button variant="outline-danger"
                    onClick={() => onclick(user_id, setLike, setMutual)}>
                <i className={`bi bi-${icon}`} style={{fontSize: 50}}/>
            </Button>
        </Col>
        <Col>
            {photos.length > 0 && <PhotoCarousel photos={photos}/>}
        </Col>
        <Col >
            <UserHeader {...{username, first_name, last_name}}/>
            {mutual && 'Взаимно'}
        </Col>
    </Row>
}

const App = ({users, likes, mutuals}) => {
    return (
        <div className="container">
            <div className="row">
                <div className="col">
                    <div className="d-grid gap-2">
                        {users.map((user) => <Line {...user} key={user.user_id}
                                                   initial_like={likes.includes(user.user_id)}
                                                   initial_mutual={mutuals.includes(user.user_id)}
                        />)}
                    </div>
                </div>
            </div>
        </div>)
}

ReactDOM.render(
    <App {...window.reactData}/>,
    document.getElementById('root')
)