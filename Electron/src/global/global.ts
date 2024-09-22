import SongArchitecture from './SongArchitecture';

namespace Global {
  export const backendBaseUrl: string = 'https://backend-api-qsyq.onrender.com';
  export const appVersion: string = '1.0.0';

  export const repositoryUrl: string =
    'https://github.com/AntonioMrtz/SpotifyElectron/';

  export const noSongPlaying = 'NOSONGPLAYING';
  export const songArchitecture: SongArchitecture =
    SongArchitecture.FILE_ARCHITECTURE;

  export interface HandleUrlChangeResponse {
    canGoBack: boolean | undefined;
    canGoForward: boolean | undefined;
  }
}
export default Global;
