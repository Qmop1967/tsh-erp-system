// This file defines TypeScript interfaces and types used throughout the application.

export interface User {
    id: string;
    name: string;
    email: string;
    role: 'admin' | 'user';
}

export interface Admin extends User {
    permissions: string[];
}

export interface ResponseData<T> {
    success: boolean;
    data: T;
    message?: string;
}