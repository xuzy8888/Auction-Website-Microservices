import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from "../config";

function Login({ onLogin }) {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post(`${config.userServiceUrl}/login`, {
                username: formData.username,
                password: formData.password
            });

            if (response.status === 200) {
                console.log('Login successful:', response.data);
                onLogin(response.data);

                try {
                    const response_log = await axios.post(`${config.logServiceUrl}/log`, {
                        msg: formData.username += ' login successfully.'
                    });
                    if (response_log.status === 200) {
                        console.log('Login information saved successfully:', response_log.data);
                    } else {
                        console.error('Login information failed to be saved:', response_log);
                    }
                } catch (error) {
                    console.error('There was an error while saving the login information:', error);
                }

                navigate('/');
            } else {
                console.error('Login failed:', response);
                alert('login failed')
            }
        } catch (error) {
            console.error('There was an error during the login process:', error);
            alert('login failed')
        }
    };

    return (
        <>
            <div className='container pt-5'>
                <div className="row mt-2">
                    <div className="col">
                        <h2>Welcome Back to JavaSavesUs Auctions!</h2>
                    </div>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className='row mt-5'>
                        <div className="col-4">
                            <label htmlFor='username' className="form-label">Username</label>
                            <input type='text' className="form-control" name='username' value={formData.username} onChange={handleChange} required />
                        </div>
                    </div>
                    <div className='row mt-4'>
                        <div className="col-4">
                            <label htmlFor='password' className="form-label">Password</label>
                            <input type='password' className="form-control" name='password' value={formData.password} onChange={handleChange} required />
                        </div>
                    </div>
                    <div className='row my-4'>
                        <div className="col-4">
                            <button type="submit" className="btn btn-danger">Log In</button>
                            <button className="btn btn-secondary" onClick={() => navigate('/register')}>I don't have a account?</button>
                        </div>
                    </div>
                </form>
            </div>
        </>
    );
}

export default Login;
