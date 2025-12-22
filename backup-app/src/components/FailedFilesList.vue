<template>
  <div v-if="hasFailedFiles" class="bg-dark-surface/50 backdrop-blur-sm rounded-lg border border-red-500/30 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-red-400">
        Файлы с ошибками ({{ failedFiles.length }})
      </h3>
      <button
        @click="retryAll"
        :disabled="inProgress"
        class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
      >
        Повторить все
      </button>
    </div>

    <div class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="file in failedFiles"
        :key="file.id"
        class="p-3 bg-dark-hover rounded border border-red-500/50"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <div class="text-white text-sm truncate">
              {{ file.name }}<span class="text-gray-400">{{ file.extension }}</span>
            </div>
            <div class="text-gray-500 text-xs mt-1 truncate">{{ file.path }}</div>
            <div class="mt-2 flex items-center gap-2">
              <div class="text-xs text-red-400">✗ Ошибка загрузки</div>
              <div v-if="getFileError(file.id)" class="text-xs text-gray-400">
                {{ getFileError(file.id) }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <a
              :href="getFileViewUrl(file)"
              target="_blank"
              rel="noopener noreferrer"
              class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center gap-1"
              title="Открыть на сайте"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              Открыть
            </a>
            <button
              @click="retryFile(file.id)"
              :disabled="inProgress"
              class="px-3 py-1.5 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-xs rounded transition-colors"
            >
              Повторить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { File } from '@/types'
import { useBackupStore } from '@/stores/backup'

const backupStore = useBackupStore()

const failedFiles = computed(() => backupStore.failedFiles)
const hasFailedFiles = computed(() => backupStore.hasFailedFiles)
const inProgress = computed(() => backupStore.inProgress)

function getFileError(fileId: string): string | undefined {
  const error = backupStore.errors.find((e) => {
    const file = backupStore.scannedFiles.find((f) => f.id === fileId)
    return file && e.file === file.name
  })
  return error?.error
}

function retryFile(fileId: string) {
  backupStore.retryFile(fileId)
}

function retryAll() {
  backupStore.retryAllFailed()
}

function getFileViewUrl(file: File): string {
  return backupStore.getFileViewUrl(file)
}
</script>

