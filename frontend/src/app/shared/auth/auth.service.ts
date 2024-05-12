import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';
import { Injectable, inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

@Injectable({
    providedIn: 'root'
})
export class AuthService {

    user: SocialUser | null = null;
    loggedIn: boolean = false;

    constructor(private router: Router, private socialAuthService: SocialAuthService) {
        this.socialAuthService.authState.subscribe((user) => {
            this.user = user;
            this.loggedIn = (user != null);
            this.router.navigate(['/']);
        });
    }

    public signOut(): void {
        this.socialAuthService.signOut();
        this.user = null;
        this.loggedIn = false;
    }

    public getToken(): string {
        return this.user?.idToken ?? '';
    }

    public canActivate(): boolean {
        // Check if the user is logged in
        if (this.loggedIn)
            return true;
        else {
            this.router.navigate(['/login']);
            return false;
        }
    }

}

export const authGuard: CanActivateFn = (route, state) => {
    return inject(AuthService).canActivate();
};