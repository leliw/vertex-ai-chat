import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface ApiUser {
    user_id?: string;
    email: string;
    firstName: string;
    lastName: string;
    termsAccepted: boolean;
    roles: string[];
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {

    constructor(private readonly httpClient: HttpClient) { }
    /**
     * Authenticate user by token in request header
     * @returns 
     */
    auth(): Observable<ApiUser> {
        return this.httpClient.get<ApiUser>('/api/auth');
    }
    /**
     * Register authenticated user 
     * @param user 
     * @returns 
     */
    register(user: ApiUser): Observable<ApiUser> {
        console.log(user);
        return this.httpClient.post<ApiUser>('/api/users/register', user);
    }
    /**
     * Get authenticated and registered user (from session)
     * @returns 
     */
    getUser(): Observable<ApiUser> {
        return this.httpClient.get<ApiUser>('/api/user');
    }
    /**
     * Logout user 
     */
    logout(): Observable<void> {
        return this.httpClient.post<void>('/api/logout', {});
    }

}
