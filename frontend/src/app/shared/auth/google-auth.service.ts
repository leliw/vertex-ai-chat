import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService, Tokens } from './auth.service';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
/**
 * Service to handle Google login
 */
export class GoogleAuthService {
    private endpoint = '/api/google/login';
    user: SocialUser | null = null;
    loggedIn: boolean = false;

    constructor(
        private router: Router,
        private httpClient: HttpClient,
        private socialAuthService: SocialAuthService,
        private authService: AuthService
    ) {
        // Subscribe for user (login) changes
        this.socialAuthService.authState.subscribe((user) => {
            // When user login
            if (user)
                // Get access and refresh tokens
                this.getTokens(user).subscribe();
            this.user = user;
            this.loggedIn = (user != null);
        });
    }
    /**
     * Get access and refresh tokens from backend after successful Google login
     * If user is not registered, redirect to register page
     * @param user 
     */
    public getTokens(user: SocialUser): Observable<Tokens> {
        return this.httpClient.post<Tokens>(this.endpoint, null, { "headers": { "Authorization": `Bearer ${user?.idToken}` } })
            .pipe(tap({
                next: (tokens) => this.authService.set_tokens(tokens["access_token"], tokens["refresh_token"]),
                error: (err) => {
                    if (err.status == 404)
                        this.router.navigate(['/register']);
                }
            }));
    }

    public signOut(): void {
        this.socialAuthService.signOut();
        this.user = null;
        this.loggedIn = false;
    }

}