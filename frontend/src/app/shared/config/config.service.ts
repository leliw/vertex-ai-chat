import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, firstValueFrom, map, of } from 'rxjs';

export interface Config {
    title: string;
    version: string;
    oauth_client_id: string;
}

@Injectable({
    providedIn: 'root',
})
export class ConfigService {

    private url = "/api/config"
    private static config: Config | undefined = undefined;

    constructor(private http: HttpClient) { }

    public getConfig(): Observable<Config> {
        return this.http.get<Config>(this.url)
            .pipe(map(c => {
                if (!c.version)
                    c.version = "0.0.1";
                localStorage.setItem('oauth_client_id', c.oauth_client_id);
                return c;
            }));
    }

    getOAuthClientId(): Promise<string> {
        const local = localStorage.getItem('oauth_client_id');
        if (local) {
            return Promise.resolve(local);
        } else {
            return firstValueFrom(this.getConfig()
                .pipe(map(c => c.oauth_client_id)));
        }
    }
    
}
