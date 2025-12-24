const DEBUG_CONSOLE_POSITION_KEY = 'debugConsole_position'
const DEBUG_CONSOLE_SIZE_KEY = 'debugConsole_size'

export const uiStorage = {
  getDebugConsolePosition(): { x: number; y: number } | null {
    const data = localStorage.getItem(DEBUG_CONSOLE_POSITION_KEY)
    if (!data) return null
    try {
      return JSON.parse(data)
    } catch {
      return null
    }
  },

  setDebugConsolePosition(position: { x: number; y: number }): void {
    localStorage.setItem(DEBUG_CONSOLE_POSITION_KEY, JSON.stringify(position))
  },

  getDebugConsoleSize(): { width: number; height: number } | null {
    const data = localStorage.getItem(DEBUG_CONSOLE_SIZE_KEY)
    if (!data) return null
    try {
      return JSON.parse(data)
    } catch {
      return null
    }
  },

  setDebugConsoleSize(size: { width: number; height: number }): void {
    localStorage.setItem(DEBUG_CONSOLE_SIZE_KEY, JSON.stringify(size))
  },
}

