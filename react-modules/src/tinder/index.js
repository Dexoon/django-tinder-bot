import React, {useState} from "react";
import ReactDOM from "react-dom";
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';
import alert from "bootstrap/js/src/alert";

const get_str = (username, first_name, last_name) => {
    let str = ' ';
    if (isNaN(username)) {
        str += `@${username} `
    }
    str += `${first_name} `;
    if (last_name) {
        str += last_name;
    }
    return str;
}
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

const Line = ({user_id, username, first_name, last_name, initial_like, initial_mutual}) => {
    const [like, setLike] = useState(initial_like);
    const [mutual, setMutual] = useState(initial_mutual);
    let variant = "danger";
    if (!like) {
        variant = 'outline-' + variant
    }
    return <div>
        <Button variant={variant} onClick={() => set_like(user_id, setLike,setMutual)}>♥</Button>
        {get_str(username, first_name, last_name)}
        {mutual && 'Взаимно'}
        {like && <Button variant="outline-dark" onClick={() => unlike(user_id, setLike, setMutual)}>❌</Button>}

    </div>
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