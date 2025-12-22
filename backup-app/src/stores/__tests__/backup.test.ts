import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBackupStore } from '../backup'
import { useAuthStore } from '../auth'
import * as scanner from '@/utils/scanner'
import * as fileSaver from '@/utils/fileSaver'
import * as cookies from '@/utils/cookies'

vi.mock('@/utils/scanner')
vi.mock('@/utils/fileSaver')
vi.mock('@/utils/cookies')
vi.mock('../auth', () => ({
  useAuthStore: vi.fn(),
}))

describe('useBackupStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    const mockAuthStore = {
      user: { username: 'testuser', isCurrentUser: true },
      sections: [{ id: '1', name: 'Test', folderName: 'test', url: '', icon: '', count: 0, type: 'pictures' }],
      selectedSections: ['1'],
      sid: 'test123',
      fullCookies: { sid: 'test123' },
      updateCookies: vi.fn(),
    }

    vi.mocked(useAuthStore).mockReturnValue(mockAuthStore as any)
  })

  it('should initialize with default state', () => {
    const store = useBackupStore()
    expect(store.saveMode).toBe('structure')
    expect(store.scannedFiles).toEqual([])
    expect(store.status).toBe('idle')
    expect(store.totalFiles).toBe(0)
    expect(store.downloadedFiles).toBe(0)
  })

  it('should compute canScan correctly', () => {
    const store = useBackupStore()
    expect(store.canScan).toBe(true)

    store.status = 'scanning'
    expect(store.canScan).toBe(false)
  })

  it('should compute canDownload correctly', () => {
    const store = useBackupStore()
    expect(store.canDownload).toBe(false)

    store.scannedFiles = [{ id: '1', name: 'test', extension: '.txt', type: 1, downloadUrl: '', path: '' }]
    expect(store.canDownload).toBe(true)
  })

  it('should reset scan state', () => {
    const store = useBackupStore()
    store.scannedFiles = [{ id: '1', name: 'test', extension: '.txt', type: 1, downloadUrl: '', path: '' }]
    store.totalFiles = 1
    store.downloadedFiles = 1
    store.status = 'completed'

    store.resetScan()

    expect(store.scannedFiles).toEqual([])
    expect(store.totalFiles).toBe(0)
    expect(store.downloadedFiles).toBe(0)
    expect(store.status).toBe('idle')
  })

  it('should set save mode', () => {
    const store = useBackupStore()
    store.setSaveMode('flat')
    expect(store.saveMode).toBe('flat')

    store.setSaveMode('structure')
    expect(store.saveMode).toBe('structure')
  })

  it('should set current page', () => {
    const store = useBackupStore()
    store.setCurrentPage(2)
    expect(store.currentPage).toBe(2)
  })

  it('should compute paginated files correctly', () => {
    const store = useBackupStore()
    store.scannedFiles = [
      { id: '1', name: 'file1', extension: '.txt', type: 1, downloadUrl: '', path: '' },
      { id: '2', name: 'file2', extension: '.txt', type: 1, downloadUrl: '', path: '' },
      { id: '3', name: 'file3', extension: '.txt', type: 1, downloadUrl: '', path: '' },
    ]
    store.filesPerPage = 2
    store.currentPage = 1

    expect(store.paginatedFiles.length).toBe(2)
    expect(store.paginatedFiles[0].id).toBe('1')
    expect(store.paginatedFiles[1].id).toBe('2')
  })

  it('should compute total pages correctly', () => {
    const store = useBackupStore()
    store.scannedFiles = Array.from({ length: 25 }, (_, i) => ({
      id: `${i}`,
      name: `file${i}`,
      extension: '.txt',
      type: 1,
      downloadUrl: '',
      path: '',
    }))
    store.filesPerPage = 10

    expect(store.totalPages).toBe(3)
  })
})

