import { HttpClient, HttpHeaders, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { BehaviorSubject, catchError, Observable, switchMap, tap, throwError } from 'rxjs';
import { jwtDecode } from "jwt-decode";
import { ValidatorFn, AbstractControl, ValidationErrors } from '@angular/forms';

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
    public store_token: boolean = false;
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
            this.decodeToken(this.refresh_token);
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
                this.set_tokens(value.access_token, value.refresh_token)
            },
            error: error => console.error('Błąd logowania:', error),
        }));
    }

    set_tokens(access_token: string, refresh_token: string): void {
        console.log(access_token)
        this.access_token = access_token;
        this.refresh_token = refresh_token
        this.decodeToken(this.access_token);
        if (this.store_token) {
            localStorage.setItem("access_token", this.access_token);
            localStorage.setItem("refresh_token", this.refresh_token);
        }
        console.log(this.redirectUrl)
        if (this.redirectUrl) {
            this.router.navigate([this.redirectUrl]);
            this.redirectUrl = undefined;
        } else {
            this.router.navigate(['/']); // Przekierowanie na stronę główną
        }
    }

    logout(): Observable<void> {
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.refresh_token}` });
        return this.http.post<void>('/api/logout', {}, { headers: headers }).pipe(tap(() => {
            this.cleanData();
            this.router.navigate(['/login']);
        }));
    }

    /**
     * Decode JWT token and set user data
     * @param token JWT token
     */
    private decodeToken(token: string): void {
        const payload: any = jwtDecode(token);
        this.username = payload.email;
        this.user_email = payload.email;
        this.roles = payload.roles;
    }

    /**
     * Clear user data and remove tokens from local storage
     */
    cleanData(): void {
        this.access_token = undefined;
        this.username = undefined;
        this.user_email = undefined;
        this.roles = [];
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
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
    if ([
        '/api/ping',
        '/api/config',
        '/api/users/register',
        '/api/login',
        '/api/google/login',
        '/api/logout',
        '/api/token-refresh',
        '/api/reset-password-request',
        '/api/reset-password'
    ].includes(req.url))
        return next(req);

    const authService = inject(AuthService);
    const router = inject(Router);
    if (!authService.isLoggedIn()) {
        router.navigate(['/login']);
        throw new Error('Brak dostępu' + req.url);
    } else {
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
                                console.log('Refresh token error:', err);
                                authService.cleanData();
                                router.navigate(['/login']);
                            }
                            throw err;
                        }))
                };
                throw err;
            }));
    }
};

/**
 * Check if new password is equal to new_password2
 * It should be used for password confirmation (second) field
 * @returns ValidatorFn
 */
export function newPasswordEuqalsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const value2: string = control.value;
        const value1: string = control.parent?.value.new_password
        return value1 != value2 ? { equals: true } : null;
    }
}

/**
 * Check if password has at least one uppercase letter, one lowercase letter and one digit
 * @param minLength Minimal password length
 * @returns 
 */
export function passwordStrengthValidator(minLength: number): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const value: string = control.value;
        if (!value) {
            return null;
        }
        if (value.length < minLength)
            return { minlength: true }
        const hasUpperCase = /[A-Z]+/.test(value);
        const hasLowerCase = /[a-z]+/.test(value);
        const hasNumeric = /\d+/.test(value);
        const passwordValid = hasUpperCase && hasLowerCase && hasNumeric;
        return !passwordValid ? { passwordStrength: true } : null;
    }
}