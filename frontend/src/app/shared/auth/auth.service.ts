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
        const jsonUser = localStorage.getItem("user")
        if (jsonUser) {
            this.user = JSON.parse(jsonUser);  
            this.loggedIn = (this.user != null);
        }
        this.socialAuthService.authState.subscribe((user) => {
            this.user = user;
            localStorage.setItem("user", JSON.stringify(user))
            this.loggedIn = (user != null);
            this.router.navigate(['/']);
        });
    }

    public signOut(): void {
        this.socialAuthService.signOut();
        this.user = null;
        localStorage.removeItem("user");
        this.loggedIn = false;
    }

    public getToken(): string {
        const jsonUser = localStorage.getItem("user")
        if (jsonUser)
            this.user = JSON.parse(jsonUser);
        return this.user?.idToken ?? '';
    }

    public canActivate(): boolean {
        // Check if the user is logged in
        this.loggedIn = localStorage.getItem("user") != null;
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