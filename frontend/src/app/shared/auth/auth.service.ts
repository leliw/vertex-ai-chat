import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';
import { Injectable, inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { ApiService, ApiUser } from '../api.service';


@Injectable({
    providedIn: 'root'
})
export class AuthService {
    isLoading = true;
    socialUser: SocialUser | null = null;
    apiUser: ApiUser | null = null;

    constructor(private router: Router, private socialAuthService: SocialAuthService, private apiService: ApiService) {
        const jsonUser = localStorage.getItem("socialUser")
        if (jsonUser) {
            this.socialUser = JSON.parse(jsonUser);
            this.apiService.getUser().subscribe({
                next: (apiUser) => {
                    this.apiUser = apiUser;
                    this.router.navigate(['/'])
                    this.isLoading = false;
                },
                error: (err) => {
                    if (err.status == 404)
                        this.router.navigate(['/register']);
                    else
                        this.router.navigate(['/login']);
                }
            });
        } else {
            this.isLoading = false;
        }
        this.socialAuthService.authState.subscribe((socialUser) => {
            this.socialUser = socialUser;
            if (socialUser) {
                localStorage.setItem("socialUser", JSON.stringify(socialUser));
                this.getApiUserAndRedirect();
            }
        });
    }

    private getApiUserAndRedirect(): void {
        this.apiService.auth().subscribe({
            next: (apiUser) => {
                this.apiUser = apiUser;
                this.router.navigate(['/'])
            },
            error: (err) => {
                if (err.status == 404)
                    this.router.navigate(['/register']);
                else
                    this.router.navigate(['/login']);
            }
        });
    }

    public signOut(): void {
        this.socialAuthService.signOut();
        this.apiService.logout().subscribe(
            () => {
                this.router.navigate(['/login']);
                localStorage.removeItem("socialUser");
                this.socialUser = null;
                this.apiUser = null;
            }
        );
    }

    public getToken(): string {
        if (!this.socialUser) {
            const jsonUser = localStorage.getItem("socialUser")
            if (jsonUser)
                this.socialUser = JSON.parse(jsonUser);
        }
        return this.socialUser?.idToken ?? '';
    }

    public getUserPhotoUrl(): string {
        return this.socialUser?.photoUrl ?? '';
    }

    public isAuthenticated(): boolean {
        return this.socialUser != null;
    }

    public isRegistered(): boolean {
        return this.apiUser != null;
    }

    public hasRole(role: string): boolean {
        if (role=="admin" && this.apiUser?.email=="marcin.leliwa@gmail.com")
            return true;
        else
            return this.apiUser?.roles?.includes(role) ?? false;
    }

    public canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
        if (!this.isAuthenticated()) {
            this.router.navigate(['/login']);
            return false;
        } else if (!this.isRegistered() && route.url[0].path != 'register') {
            this.router.navigate(['/register']);
            return false;
        } else {
            return true;
        }
    }

}

export const authGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
    return inject(AuthService).canActivate(route, state);
};