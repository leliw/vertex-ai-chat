import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UserHeader {
    user_id: string;
    email: string;
    name: string;
    firstName: string | undefined;
    lastName: string | undefined;
}

export interface User extends UserHeader {
    termsAccepted: boolean;
    pictureUrl: string | undefined;
}



@Injectable({
    providedIn: 'root'
})
export class UserService {
    private apiUrl = '/api/users';

    constructor(private http: HttpClient) { }

    getUser(): Observable<User> {
        return this.http.get<User>(this.apiUrl);
    }

    getUsers(): Observable<UserHeader[]> {
        return this.http.get<UserHeader[]>(this.apiUrl);
    }
}
