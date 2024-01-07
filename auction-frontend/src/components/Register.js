import React, { useState } from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import config from "../config";

function Register() {
    const [formData, setFormData] = useState({
        fname: '',
        lname: '',
        email: '',
        username: '',
        password: '',
        confirmPassword: ''
    });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        try {
            const response = await axios.post(`${config.userServiceUrl}/register`, {
                username: formData.username,
                password: formData.password,
                confirm_password: formData.confirmPassword,
                fname: formData.fname,
                lname: formData.lname,
                email: formData.email
            });

            if (response.data.success) {
                alert('Registration successful');
                navigate('/login');
            }
        } catch (error) {
            alert('An error occurred during registration');
        }
    };

    return (
        <>
            <div className='container pt-5'>
                <div className="row mt-2">
                    <div className="col">
                        <h2>Enter your details below to create an account!</h2>
                    </div>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className='row mt-5'>
                        <div className="col-4">
                            <label htmlFor='fname' className="form-label">First Name</label>
                            <input type='text' className="form-control" name='fname' value={formData.fname} onChange={handleChange} />
                        </div>
                        <div className="col-4">
                            <label htmlFor='lname' className="form-label">Last Name</label>
                            <input type='text' className="form-control" name='lname' value={formData.lname} onChange={handleChange} />
                        </div>
                    </div>
                    <div className='row mt-4'>
                        <div className="col-4">
                            <label htmlFor='email' className="form-label">Email</label>
                            <input type='email' className="form-control" name='email' value={formData.email} onChange={handleChange} />
                        </div>
                    </div>
                    <div className='row mt-4'>
                        <div className="col-4">
                            <label htmlFor='username' className="form-label">Enter a Username:</label>
                            <input type='text' className="form-control" name='username' value={formData.username} onChange={handleChange} />
                        </div>
                    </div>
                    <div className='row mt-4'>
                        <div className="col-4">
                            <label htmlFor='password' className="form-label">Enter a Password:</label>
                            <input type='password' className="form-control" name='password' value={formData.password} onChange={handleChange} />
                        </div>
                    </div>
                    <div className='row mt-4'>
                        <div className="col-4">
                            <label htmlFor='confirmPassword' className="form-label">Confirm Password:</label>
                            <input type='password' className="form-control" name='confirmPassword' value={formData.confirmPassword} onChange={handleChange} />
                        </div>
                    </div>
                    <div className='row my-4'>
                        <div className="col-4">
                            <button type="submit" className="btn btn-danger">Create Account</button>
                            <button className="btn btn-secondary" onClick={() => navigate('/login')}>Already a User?</button>
                        </div>
                    </div>
                </form>
            </div>
        </>
    );
}

export default Register;
