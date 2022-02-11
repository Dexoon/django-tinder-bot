import React from "react";
import ReactDOM from "react-dom";
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';

const App = ({data: {chats}}) => {
    return (
        <div className="container">
            <center><h2>Выберите чат</h2></center>
            <br/>
            <div className="row">
                <div className="col">
                    <div className="d-grid gap-2">
                        {chats.map(({id, title}) => <Button variant="primary" size="lg" href={`chat/${id}/`}>
                                {title}
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        </div>)
}

ReactDOM.render(
    <App data={window.reactData}/>,
    document.getElementById('root')
)