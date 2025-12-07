## Week 7: Secure Authentication System

Student Name: Farhan Rais shaikh 

Student ID: M01037321

Course: BSc Information Technology

## Overview

A simple command-line authentication system using secure password hashing. Users can register with roles, log in safely, and maintain active sessions.

## Features

- bcrypt password hashing with auto-salting

- Role-based registration (user, admin, analyst)

- Login with password verification

- Password strength check

- Username & password validation

- 3-attempt lockout with 5-minute cooldown

- Session tokens for active users

- File-based storage (users.txt, sessions.txt, failed_attempts.txt)

## Technical Notes

- Uses bcrypt for one-way hashing

- Stores user and session data in plain text files

- Username: 3–20 chars (alphanumeric + underscore)

- Password: 6–50 chars with required complexity
