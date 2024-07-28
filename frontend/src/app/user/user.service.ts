import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UserHeader {
    user_id: string;
    email: string;
    given_name: string | undefined;
    family_name: string | undefined;
    roles: string[] | undefined
}

export interface User extends UserHeader {
    terms_accepted: boolean;
    picture: string | undefined;
}



@Injectable({
    providedIn: 'root'
})
export class UserService {
    private apiUrl = '/api/users';

    constructor(private http: HttpClient) { }

    getUser(email: string): Observable<User> {
        return this.http.get<User>(`${this.apiUrl}/${email}`);
    }

    getUsers(): Observable<UserHeader[]> {
        return this.http.get<UserHeader[]>(this.apiUrl);
    }

    updateUser(email: string, user: User): Observable<User> {
        return this.http.put<User>(`${this.apiUrl}/${email}`, user);
    }

    deleteUser(email: string): Observable<boolean> {
        return this.http.delete<boolean>(`${this.apiUrl}/${email}`);
    }
}

