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
        const jsonConfig = localStorage.getItem('config');
        if (jsonConfig) {
            return of(JSON.parse(jsonConfig));
        } else {
            return this.http.get<Config>(this.url)
                .pipe(map(c => {
                    if (!c.version)
                        c.version = "0.0.1";
                    localStorage.setItem('config', JSON.stringify(c));
                    return c;
                }));
        }
    }

    getOAuthClientId(): Promise<string> {
        return firstValueFrom(this.getConfig()
            .pipe(map(c => c.oauth_client_id)));
    }
}
