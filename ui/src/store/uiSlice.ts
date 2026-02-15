import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ThemeMode } from '@types';

interface UiState {
  themeMode: ThemeMode;
  sidebarOpen: boolean;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;
}

const initialState: UiState = {
  themeMode: 'light',
  sidebarOpen: true,
  notifications: []
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleTheme(state: UiState) {
      state.themeMode = state.themeMode === 'light' ? 'dark' : 'light';
    },
    setTheme(state: UiState, action: PayloadAction<ThemeMode>) {
      state.themeMode = action.payload;
    },
    toggleSidebar(state: UiState) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen(state: UiState, action: PayloadAction<boolean>) {
      state.sidebarOpen = action.payload;
    },
    addNotification(state: UiState, action: PayloadAction<{
      type: 'success' | 'error' | 'warning' | 'info';
      message: string;
      duration?: number;
    }>) {
      const notification = {
        id: Date.now().toString(),
        ...action.payload
      };
      state.notifications.push(notification);
    },
    removeNotification(state: UiState, action: PayloadAction<string>) {
      state.notifications = state.notifications.filter((n: any) => n.id !== action.payload);
    }
  }
});

export const {
  toggleTheme,
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  addNotification,
  removeNotification
} = uiSlice.actions;

export default uiSlice.reducer;
