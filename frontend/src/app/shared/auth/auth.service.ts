import { HttpClient, HttpHeaders, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { BehaviorSubject, catchError, Observable, switchMap, tap, throwError } from 'rxjs';
import { jwtDecode } from "jwt-decode";

export interface Tokens {
    access_token: string;
    refresh_token: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {

    public username?: string;
    public user_email?: string;
    private redirectUrl?: string;
    public roles?: string[];
    public access_token?: string;
    public refresh_token?: string;

    private isRefreshing = false;
    private readonly refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);


    constructor(private readonly http: HttpClient, private readonly router: Router) { }

    isLoggedIn(): boolean {
        if (this.username)
            return true;
        this.access_token = localStorage.getItem("access_token") ?? undefined
        this.refresh_token = localStorage.getItem("refresh_token") ?? undefined
        if (this.refresh_token) {
            const payload: any = jwtDecode(this.refresh_token);
            this.username = payload.name;
            this.user_email = payload.email;
            this.roles = payload.roles;
            return true;
        }
        return false;
    }

    login(credentials: any): Observable<any> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        return this.http.post<Tokens>('/api/login', formData).pipe(tap({
            next: value => {
                this.access_token = value.access_token;
                this.refresh_token = value.refresh_token
                const payload: any = jwtDecode(this.access_token);
                this.username = payload.name;
                this.user_email = payload.email;
                this.roles = payload.roles;
                if (credentials.store_token) {
                    localStorage.setItem("access_token", this.access_token);
                    localStorage.setItem("refresh_token", this.refresh_token);
                }
            },
            complete: () => {
                if (this.redirectUrl) {
                    this.router.navigate([this.redirectUrl]);
                    this.redirectUrl = undefined;
                } else {
                    this.router.navigate(['/']); // Przekierowanie na stronę główną
                }
            },
            error: error => console.error('Błąd logowania:', error),
        }));
    }

    logout(): Observable<void> {
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.refresh_token}` });
        return this.http.post<void>('/api/logout', { headers: headers }).pipe(tap(() => {
            this.access_token = undefined;
            this.username = undefined;
            this.user_email = undefined
            this.roles = []
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            this.router.navigate(['/login']);
        }));
    }

    resetPasswordRequest(email: string): Observable<void> {
        return this.http.post<void>("/api/reset-password-request", { email: email });
    }

    resetPassword(email: string, reset_code: string, new_password: string): Observable<void> {
        return this.http.post<void>("/api/reset-password", {
            email: email,
            reset_code: reset_code,
            new_password: new_password
        });
    }

    changePassword(old_password: string, new_password: string): Observable<void> {
        return this.http.post<void>('/api/change-password', {
            old_password: old_password,
            new_password: new_password
        });
    }

    public canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
        if (!this.isLoggedIn) {
            this.redirectUrl = state.url
            this.router.navigate(['/login']);
            return false;
        } else {
            const role = route.data['role']
            if (!role || this.hasRole(role))
                return true;
            else
                return false;
        }
    }

    public hasRole(role: string): boolean {
        return this.roles ? this.roles.includes(role) : false;
    }

    public hasAllRoles(roles: string[]): boolean {
        return roles.every(role => this.hasRole(role))
    }

    public hasAnyRoles(roles: string[]): boolean {
        return roles.some(role => this.hasRole(role))
    }

    public getBlob(url: string): Observable<Blob> {
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.access_token}` });
        return this.http.get(url, { headers: headers, responseType: 'blob' });
    }

    refreshTokens(): Observable<any> {
        if (this.isRefreshing)
            return this.refreshTokenSubject.asObservable();
        this.isRefreshing = true;

        const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.refresh_token}` });
        return this.http.post<Tokens>('/api/token-refresh', {}, { headers: headers }).pipe(
            catchError(error => {
                this.refreshTokenSubject.next(null);
                this.isRefreshing = false;
                return throwError(() => error);
            }),
            tap(tokens => {
                this.refreshTokenSubject.next(tokens);
                this.isRefreshing = false;
                this.access_token = tokens.access_token;
                this.refresh_token = tokens.refresh_token;
                localStorage.setItem("access_token", this.access_token);
                localStorage.setItem("refresh_token", this.refresh_token);
            }));
    }

}

export const authGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
    return inject(AuthService).canActivate(route, state);
};


export const authInterceptor: HttpInterceptorFn = (req, next) => {
    if (req.url.endsWith('/api/config') || req.url.endsWith('/api/login') || req.url.endsWith('/api/token-refresh')) {
        return next(req);
    } else {
        const authService = inject(AuthService);
        const router = inject(Router);

        // Clone the request and add the authorization header
        const authReq = req.clone({
            setHeaders: {
                Authorization: `Bearer ${authService.access_token}`
            }
        });
        return next(authReq).pipe(
            catchError(err => {
                if (err.status === 401) {
                    return authService.refreshTokens().pipe(
                        switchMap(() => {
                            const authReq = req.clone({
                                setHeaders: {
                                    Authorization: `Bearer ${authService.access_token}`
                                }
                            });
                            return next(authReq);
                        }),
                        catchError(err => {
                            if (err.status === 401) {
                                router.navigate(['/login']);
                            }
                            throw err;
                        }))
                };
                throw err;
            }));
    }
};