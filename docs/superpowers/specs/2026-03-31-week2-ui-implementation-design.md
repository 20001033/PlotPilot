# Week 2: UI实现与AI功能集成设计文档

**项目**: aitext - AI驱动的小说创作系统
**功能**: 主页侧边栏、工作台顶部条、核心图表组件、AI任务集成、代码重构
**日期**: 2026-03-31
**版本**: 1.0

---

## 目录

1. [概述](#概述)
2. [设计目标](#设计目标)
3. [架构设计](#架构设计)
4. [UI组件设计](#ui组件设计)
5. [AI功能集成](#ai功能集成)
6. [图表组件设计](#图表组件设计)
7. [代码重构方案](#代码重构方案)
8. [实施计划](#实施计划)
9. [技术细节](#技术细节)

---

## 概述

### 项目背景

Week 1已完成基础设施搭建：
- ✅ 后端三层架构（Router-Service-Repository）
- ✅ 统一错误处理和日志系统
- ✅ 统计API（4个端点）
- ✅ 前端类型定义、API客户端、Pinia Store
- ✅ ECharts配置
- ✅ 89个测试全部通过

### Week 2目标

在Week 1基础上实现：
1. **UI组件**：主页侧边栏、工作台顶部条、统计卡片
2. **图表组件**：进度图、趋势图、分布图、关系图
3. **AI集成**：任务状态追踪、实时进度更新、智能缓存失效
4. **代码重构**：Workbench.vue拆分、Chapter.vue优化、vis-network迁移
5. **代码清理**：删除旧代码、移除废弃依赖

---

## 设计目标

### 功能目标

1. **可视化统计数据**
   - 主页显示全局统计（总书籍、总章节、总字数、各阶段分布）
   - 工作台显示当前书籍统计（字数、进度、完成率、写作趋势）

2. **AI任务可视化**
   - 实时显示运行中的AI任务（规划/写作/运行）
   - 显示任务进度和当前阶段
   - 任务完成后自动刷新统计数据

3. **图表展示**
   - 章节进度条形图
   - 字数趋势折线图
   - 内容分布饼图
   - 人物关系图（替换vis-network）

4. **代码质量提升**
   - 拆分大型组件（Workbench.vue 400+行 → 4个子组件）
   - 优化性能（并行请求、防抖渲染）
   - 统一图表库（移除vis-network，全部使用ECharts）

### 非功能目标

1. **性能**
   - 统计数据缓存，避免重复请求
   - 图表懒加载，按需渲染
   - Markdown渲染防抖（300ms）

2. **用户体验**
   - 加载状态提示（骨架屏）
   - 错误处理和重试机制
   - 响应式布局（桌面/平板）

3. **可维护性**
   - 组件职责单一，易于测试
   - 代码复用（通用StatCard组件）
   - 清晰的文件结构

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                     │
├─────────────────────────────────────────────────────────┤
│  Pages                                                   │
│  ├── Home.vue                                           │
│  │   ├── StatsSidebar.vue (新增)                       │
│  │   │   └── StatCard.vue × 4 (新增)                   │
│  │   └── 现有内容区域                                   │
│  │                                                       │
│  └── Workbench.vue (重构)                               │
│      ├── StatsTopBar.vue (新增)                         │
│      │   ├── StatItem × 6                               │
│      │   └── JobStatusIndicator.vue (新增)              │
│      ├── ChapterList.vue (拆分)                         │
│      ├── ChatArea.vue (拆分)                            │
│      └── SettingsPanel.vue (拆分)                       │
├─────────────────────────────────────────────────────────┤
│  Components                                              │
│  ├── stats/                                             │
│  │   ├── StatCard.vue (通用统计卡片)                   │
│  │   ├── StatsSidebar.vue (主页侧边栏)                 │
│  │   ├── StatsTopBar.vue (工作台顶部条)                │
│  │   └── JobStatusIndicator.vue (AI任务状态)           │
│  │                                                       │
│  └── charts/                                            │
│      ├── ProgressChart.vue (章节进度)                   │
│      ├── TrendChart.vue (字数趋势)                      │
│      ├── DistributionChart.vue (内容分布)               │
│      └── GraphChart.vue (关系图，替换vis-network)       │
├─────────────────────────────────────────────────────────┤
│  Composables                                             │
│  ├── useWorkbench.ts (工作台业务逻辑)                   │
│  ├── useJobStatus.ts (任务状态追踪)                     │
│  └── useStatsRefresh.ts (统计刷新逻辑)                  │
├─────────────────────────────────────────────────────────┤
│  Store (Pinia)                                           │
│  └── statsStore.ts (Week 1已实现)                       │
│      ├── State: globalStats, bookStatsCache, loading    │
│      ├── Actions: loadGlobalStats, loadBookStats        │
│      └── 新增: onJobCompleted, onChapterSaved           │
├─────────────────────────────────────────────────────────┤
│  API Client                                              │
│  ├── stats.ts (Week 1已实现)                            │
│  └── book.ts (Week 1已实现，含jobApi)                   │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
├─────────────────────────────────────────────────────────┤
│  Routers                                                 │
│  ├── /api/stats/* (Week 1已实现)                        │
│  └── /api/jobs/* (已存在)                               │
├─────────────────────────────────────────────────────────┤
│  Services                                                │
│  ├── StatsService (Week 1已实现)                        │
│  └── Job System (已存在)                                │
├─────────────────────────────────────────────────────────┤
│  Repositories                                            │
│  └── StatsRepository (Week 1已实现)                     │
└─────────────────────────────────────────────────────────┘
```

### 数据流

**1. 统计数据流：**
```
组件挂载
  ↓
调用 statsStore.loadGlobalStats() / loadBookStats()
  ↓
检查缓存 → 有缓存：直接返回
  ↓
无缓存：调用 statsApi.getGlobal() / getBook()
  ↓
API请求 → /api/stats/global 或 /api/stats/book/{slug}
  ↓
后端返回数据
  ↓
Store更新状态 + 缓存
  ↓
组件响应式更新
```

**2. AI任务状态流：**
```
用户触发任务（规划/写作/运行）
  ↓
调用 jobApi.startPlan() / startWrite() / startRun()
  ↓
返回 job_id
  ↓
JobStatusIndicator开始轮询（每3秒）
  ↓
调用 jobApi.getStatus(job_id)
  ↓
检查 status.done
  ↓
done=false: 更新进度显示，继续轮询
  ↓
done=true: 停止轮询，触发completed事件
  ↓
statsStore.onJobCompleted(slug)
  ↓
清除缓存 + 强制刷新统计
  ↓
UI更新显示最新数据
```

**3. 缓存失效流：**
```
触发事件：
├── 任务完成 → clearCache(slug) + loadBookStats(slug, true)
├── 章节保存 → clearCache(slug) + loadChapterStats(slug, chapterId, true)
├── 手动刷新 → clearCache() + loadGlobalStats(true)
└── 离开页面 → 保留缓存（下次访问可用）
```

---

## UI组件设计

### 1. StatCard.vue (统计卡片)

**用途：** 通用的统计数据展示卡片

**Props：**
```typescript
interface StatCardProps {
  title: string                    // 卡片标题
  value: number | string           // 主要数值
  icon?: string                    // 图标（emoji或图标类名）
  trend?: {                        // 趋势指示（可选）
    value: number                  // 变化值
    direction: 'up' | 'down'       // 方向
  }
  loading?: boolean                // 加载状态
  unit?: string                    // 单位（如"本"、"章"、"字"）
}
```

**样式特点：**
- 白色卡片，圆角8px，hover时阴影加深
- 图标在左上角（32px）
- 数值大号显示（32px，粗体）
- 标题小字（14px，灰色）
- 趋势箭头和百分比（绿色↑/红色↓）
- 加载时显示骨架屏动画

**示例：**
```vue
<StatCard
  title="总书籍数"
  :value="5"
  icon="📚"
  unit="本"
  :trend="{ value: 2, direction: 'up' }"
/>
```

### 2. StatsSidebar.vue (主页侧边栏)

**用途：** 主页左侧固定侧边栏，显示全局统计

**布局：**
- 固定宽度：280px
- 位置：左侧，从顶部到底部
- 背景：浅灰色（#f5f5f5）
- 内边距：24px

**内容结构：**
```vue
<template>
  <aside class="stats-sidebar">
    <header class="sidebar-header">
      <h2 class="sidebar-title">数据概览</h2>
      <n-button text size="small" @click="refresh">
        <template #icon><RefreshIcon /></template>
      </n-button>
    </header>

    <div class="stats-cards">
      <StatCard
        title="总书籍数"
        :value="globalStats?.total_books"
        icon="📚"
        unit="本"
        :loading="loading"
      />
      <StatCard
        title="总章节数"
        :value="globalStats?.total_chapters"
        icon="📄"
        unit="章"
        :loading="loading"
      />
      <StatCard
        title="总字数"
        :value="formatNumber(globalStats?.total_words)"
        icon="✍️"
        unit="字"
        :loading="loading"
      />
      <StatCard
        title="各阶段书籍"
        :value="formatStages(globalStats?.books_by_stage)"
        icon="📊"
        :loading="loading"
      />
    </div>

    <footer class="sidebar-footer">
      <n-text depth="3" size="small">
        最后更新：{{ formatTime(lastUpdate) }}
      </n-text>
    </footer>
  </aside>
</template>
```

**数据来源：**
```typescript
const statsStore = useStatsStore()
const { globalStats, loading } = storeToRefs(statsStore)

onMounted(() => {
  statsStore.loadGlobalStats()
})

const refresh = () => {
  statsStore.loadGlobalStats(true) // force refresh
}
```

**集成到Home.vue：**
```vue
<template>
  <div class="home">
    <StatsSidebar />
    <div class="home-content">
      <!-- 现有内容：创建表单 + 书籍列表 -->
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  min-height: 100vh;
}

.home-content {
  flex: 1;
  margin-left: 280px; /* 侧边栏宽度 */
}
</style>
```

### 3. StatsTopBar.vue (工作台顶部条)

**用途：** 工作台顶部横向统计条，显示当前书籍统计和AI任务状态

**布局：**
- 全宽，高度：自适应（约80-100px）
- 背景：渐变（从#e0f2fe到#ede9fe）
- 内边距：16px 24px
- 两行布局（桌面）或滚动布局（平板）

**内容结构：**
```vue
<template>
  <div class="stats-top-bar">
    <!-- 第一行：书籍核心统计 -->
    <div class="stats-row">
      <StatItem
        icon="📝"
        label="总字数"
        :value="formatNumber(bookStats?.total_words)"
        :loading="loading"
      />
      <StatItem
        icon="✅"
        label="完成章节"
        :value="`${bookStats?.completed_chapters}/${bookStats?.total_chapters}`"
        :loading="loading"
      />
      <StatItem
        icon="📈"
        label="完成率"
        :value="formatPercent(bookStats?.completion_rate)"
        :loading="loading"
      />
    </div>

    <!-- 第二行：写作进度 + AI任务状态 -->
    <div class="stats-row">
      <StatItem
        icon="🕐"
        label="最后更新"
        :value="formatTime(bookStats?.last_updated)"
        :loading="loading"
      />
      <StatItem
        icon="📅"
        label="今日字数"
        :value="todayWords || '--'"
        :loading="loading"
      />
      <StatItem
        icon="📊"
        label="本周字数"
        :value="weekWords || '--'"
        :loading="loading"
      />

      <!-- AI任务状态指示器 -->
      <JobStatusIndicator
        v-if="activeJob"
        :job-id="activeJob.job_id"
        @completed="onJobCompleted"
      />
    </div>
  </div>
</template>
```

**StatItem子组件：**
```vue
<template>
  <div class="stat-item">
    <span class="stat-icon">{{ icon }}</span>
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">
        <n-skeleton v-if="loading" text :width="60" />
        <span v-else>{{ value }}</span>
      </div>
    </div>
  </div>
</template>
```

**数据来源：**
```typescript
const route = useRoute()
const slug = computed(() => route.params.slug as string)
const statsStore = useStatsStore()
const { getBookStats, loading } = storeToRefs(statsStore)

const bookStats = computed(() => getBookStats.value(slug.value))

// 今日/本周字数（Week 1返回空数组，显示"--"）
const todayWords = computed(() => {
  const progress = statsStore.getProgress(slug.value)
  // TODO: 计算今日字数
  return null
})

onMounted(() => {
  statsStore.loadBookStats(slug.value)
})

const onJobCompleted = () => {
  statsStore.onJobCompleted(slug.value)
}
```

### 4. JobStatusIndicator.vue (AI任务状态指示器)

**用途：** 显示运行中的AI任务状态和进度

**Props：**
```typescript
interface JobStatusIndicatorProps {
  jobId: string  // 任务ID
}

interface JobStatusIndicatorEmits {
  (e: 'completed', status: JobStatus): void  // 任务完成事件
}
```

**UI设计：**
```vue
<template>
  <div class="job-status-indicator">
    <div class="job-icon">
      <n-spin :size="20" />
    </div>
    <div class="job-content">
      <div class="job-type">{{ jobTypeLabel }}</div>
      <div class="job-progress">{{ jobStatus?.message || '处理中...' }}</div>
    </div>
    <n-button text size="small" @click="cancelJob">取消</n-button>
  </div>
</template>
```

**轮询逻辑：**
```typescript
const jobStatus = ref<JobStatus | null>(null)
const pollInterval = ref<number | null>(null)

const pollJobStatus = async () => {
  try {
    const status = await jobApi.getStatus(props.jobId)
    jobStatus.value = status

    if (status.done) {
      stopPolling()
      emit('completed', status)

      if (status.status === 'error') {
        window.$message.error(`任务失败：${status.error}`)
      } else {
        window.$message.success('任务完成！')
      }
    }
  } catch (error) {
    console.error('Failed to poll job status:', error)
  }
}

const startPolling = () => {
  pollJobStatus() // 立即执行一次
  pollInterval.value = setInterval(pollJobStatus, 3000) // 每3秒轮询
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

const cancelJob = async () => {
  try {
    await jobApi.cancelJob(props.jobId)
    stopPolling()
    window.$message.info('任务已取消')
  } catch (error) {
    window.$message.error('取消失败')
  }
}
```

**任务类型标签：**
```typescript
const jobTypeLabel = computed(() => {
  const kind = jobStatus.value?.kind
  const labels = {
    plan: '🎯 规划中',
    write: '✍️ 写作中',
    run: '🚀 运行中'
  }
  return labels[kind] || '⚙️ 处理中'
})
```

---

## AI功能集成

### 1. AI任务生命周期

**任务状态：**
```
queued (排队) → running (运行中) → done (完成) / error (错误) / cancelled (已取消)
```

**任务类型：**
- **plan**: 生成bible.json和outline.json
- **write**: 写作指定章节范围
- **run**: 完整流程（规划→写作→导出）

**关键数据：**
```typescript
interface JobStatus {
  status: 'queued' | 'running' | 'done' | 'error' | 'cancelled'
  message?: string      // 进度消息（如"正在生成第3章"）
  phase?: string        // 当前阶段（如"beats", "draft", "summary"）
  error?: string        // 错误信息
  done?: boolean        // 是否完成
}
```

### 2. 任务检测机制

**检测运行中的任务：**

由于后端没有"获取书籍当前任务"的API，需要在前端维护任务状态：

```typescript
// 在Workbench.vue中
const activeJobId = ref<string | null>(null)

// 启动任务时保存job_id
const startPlan = async () => {
  const result = await jobApi.startPlan(slug.value)
  activeJobId.value = result.job_id
}

// 任务完成时清除
const onJobCompleted = () => {
  activeJobId.value = null
  statsStore.onJobCompleted(slug.value)
}

// 页面刷新时从localStorage恢复
onMounted(() => {
  const savedJobId = localStorage.getItem(`job_${slug.value}`)
  if (savedJobId) {
    // 检查任务是否仍在运行
    jobApi.getStatus(savedJobId).then(status => {
      if (!status.done) {
        activeJobId.value = savedJobId
      } else {
        localStorage.removeItem(`job_${slug.value}`)
      }
    })
  }
})

// 保存到localStorage
watch(activeJobId, (newId) => {
  if (newId) {
    localStorage.setItem(`job_${slug.value}`, newId)
  } else {
    localStorage.removeItem(`job_${slug.value}`)
  }
})
```

### 3. 统计数据刷新策略

**触发刷新的场景：**

1. **AI任务完成**
   ```typescript
   // JobStatusIndicator.vue
   const onJobCompleted = (status: JobStatus) => {
     emit('completed', status)
   }

   // Workbench.vue
   const handleJobCompleted = () => {
     activeJobId.value = null
     statsStore.onJobCompleted(slug.value)
   }

   // statsStore.ts
   onJobCompleted(slug: string) {
     // 清除该书籍的缓存
     delete this.bookStatsCache[slug]
     // 强制刷新
     this.loadBookStats(slug, true)
     // 同时刷新全局统计
     this.loadGlobalStats(true)
   }
   ```

2. **章节保存**
   ```typescript
   // Chapter.vue
   const saveChapter = async () => {
     await chapterApi.saveBody(slug.value, chapterId.value, content.value)
     // 触发统计刷新
     statsStore.onChapterSaved(slug.value, chapterId.value)
   }

   // statsStore.ts
   onChapterSaved(slug: string, chapterId: string) {
     // 清除缓存
     delete this.bookStatsCache[slug]
     // 刷新书籍统计
     this.loadBookStats(slug, true)
   }
   ```

3. **手动刷新**
   ```typescript
   // StatsSidebar.vue
   const refresh = () => {
     statsStore.loadGlobalStats(true)
   }

   // StatsTopBar.vue
   const refresh = () => {
     statsStore.loadBookStats(slug.value, true)
   }
   ```

**缓存策略：**
- 全局统计：缓存5分钟
- 书籍统计：缓存3分钟
- 任务完成/章节保存：立即失效
- 页面切换：保留缓存

---

## 图表组件设计

### 1. ProgressChart.vue (章节进度条形图)

**用途：** 显示各章节的完成进度

**数据来源：**
```typescript
interface ChapterProgress {
  chapter_id: string
  title: string
  progress: number  // 0-100
  status: 'draft' | 'review' | 'done'
}
```

**ECharts配置：**
```typescript
const option = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    max: 100,
    axisLabel: { formatter: '{value}%' }
  },
  yAxis: {
    type: 'category',
    data: props.data.map(d => d.title)
  },
  series: [{
    type: 'bar',
    data: props.data.map(d => ({
      value: d.progress,
      itemStyle: {
        color: d.status === 'done' ? '#10b981' :
               d.status === 'review' ? '#f59e0b' : '#3b82f6'
      }
    })),
    barWidth: '60%'
  }]
}))
```

**Props：**
```typescript
interface ProgressChartProps {
  data: ChapterProgress[]
  loading?: boolean
}
```

### 2. TrendChart.vue (字数趋势折线图)

**用途：** 显示累计字数随时间的变化

**数据来源：**
```typescript
interface TrendData {
  date: string      // YYYY-MM-DD
  words: number     // 累计字数
}
```

**ECharts配置：**
```typescript
const option = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => {
      const data = params[0]
      return `${data.name}<br/>字数: ${data.value.toLocaleString()}`
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.date),
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: '{value}' }
  },
  series: [{
    type: 'line',
    data: props.data.map(d => d.words),
    smooth: true,
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
          { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
        ]
      }
    },
    lineStyle: { color: '#3b82f6', width: 2 }
  }]
}))
```

**Props：**
```typescript
interface TrendChartProps {
  data: TrendData[]
  loading?: boolean
}
```

### 3. DistributionChart.vue (内容分布饼图)

**用途：** 显示书籍各阶段的分布

**数据来源：**
```typescript
interface DistributionData {
  name: string      // 阶段名称
  value: number     // 数量
}
```

**ECharts配置：**
```typescript
const option = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],  // 环形图
    avoidLabelOverlap: false,
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}: {d}%'
    },
    emphasis: {
      label: { show: true, fontSize: 16, fontWeight: 'bold' }
    },
    data: props.data,
    color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
  }]
}))
```

**Props：**
```typescript
interface DistributionChartProps {
  data: DistributionData[]
  loading?: boolean
}
```

### 4. GraphChart.vue (人物关系图)

**用途：** 替换vis-network，显示人物关系网络

**数据来源：**
```typescript
interface GraphNode {
  id: string
  name: string
  category?: string
}

interface GraphEdge {
  source: string
  target: string
  value?: number  // 关系强度
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}
```

**ECharts配置：**
```typescript
const option = computed(() => ({
  tooltip: {
    formatter: (params: any) => {
      if (params.dataType === 'node') {
        return `${params.data.name}`
      } else {
        return `${params.data.source} → ${params.data.target}`
      }
    }
  },
  series: [{
    type: 'graph',
    layout: 'force',
    data: props.data.nodes.map(node => ({
      id: node.id,
      name: node.name,
      symbolSize: 50,
      category: node.category
    })),
    links: props.data.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      value: edge.value || 1
    })),
    categories: [
      { name: '主角' },
      { name: '配角' },
      { name: '其他' }
    ],
    roam: true,
    label: {
      show: true,
      position: 'right',
      formatter: '{b}'
    },
    labelLayout: {
      hideOverlap: true
    },
    lineStyle: {
      color: 'source',
      curveness: 0.3
    },
    emphasis: {
      focus: 'adjacency',
      lineStyle: { width: 10 }
    },
    force: {
      repulsion: 100,
      edgeLength: [50, 100]
    }
  }]
}))
```

**Props：**
```typescript
interface GraphChartProps {
  data: GraphData
  loading?: boolean
}
```

---

## 代码重构方案

### 1. Workbench.vue 拆分

**当前问题：**
- 400+行单文件
- 混合章节列表、聊天区、设定面板逻辑
- 状态管理混乱
- 难以维护和测试

**拆分策略：**

```
Workbench.vue (主容器，100行)
├── StatsTopBar.vue (顶部统计条，80行)
├── ChapterList.vue (章节导航，150行)
├── ChatArea.vue (对话区域，200行)
└── SettingsPanel.vue (设定面板，150行)
```

**Workbench.vue (重构后)：**
```vue
<template>
  <div class="workbench">
    <StatsTopBar :slug="slug" :active-job-id="activeJobId" @job-completed="handleJobCompleted" />

    <div class="workbench-content">
      <ChapterList :slug="slug" :chapters="chapters" @select="handleChapterSelect" />
      <ChatArea :slug="slug" :messages="messages" @send="handleSendMessage" />
      <SettingsPanel :slug="slug" :settings="settings" @update="handleUpdateSettings" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useWorkbench } from '@/composables/useWorkbench'

const props = defineProps<{ slug: string }>()

const {
  chapters,
  messages,
  settings,
  activeJobId,
  handleChapterSelect,
  handleSendMessage,
  handleUpdateSettings,
  handleJobCompleted
} = useWorkbench(props.slug)
</script>
```

**useWorkbench.ts (业务逻辑提取)：**
```typescript
export function useWorkbench(slug: string) {
  const chapters = ref<Chapter[]>([])
  const messages = ref<Message[]>([])
  const settings = ref<Settings | null>(null)
  const activeJobId = ref<string | null>(null)

  // 加载数据
  const loadData = async () => {
    const [chaptersData, messagesData, settingsData] = await Promise.all([
      chapterApi.getList(slug),
      chatApi.getMessages(slug),
      settingsApi.get(slug)
    ])
    chapters.value = chaptersData
    messages.value = messagesData
    settings.value = settingsData
  }

  // 恢复任务状态
  const restoreJobState = async () => {
    const savedJobId = localStorage.getItem(`job_${slug}`)
    if (savedJobId) {
      const status = await jobApi.getStatus(savedJobId)
      if (!status.done) {
        activeJobId.value = savedJobId
      } else {
        localStorage.removeItem(`job_${slug}`)
      }
    }
  }

  // 事件处理
  const handleChapterSelect = (chapterId: string) => {
    // 导航到章节页面
  }

  const handleSendMessage = async (content: string) => {
    // 发送消息
  }

  const handleUpdateSettings = async (newSettings: Settings) => {
    // 更新设定
  }

  const handleJobCompleted = () => {
    activeJobId.value = null
    statsStore.onJobCompleted(slug)
  }

  onMounted(() => {
    loadData()
    restoreJobState()
  })

  return {
    chapters,
    messages,
    settings,
    activeJobId,
    handleChapterSelect,
    handleSendMessage,
    handleUpdateSettings,
    handleJobCompleted
  }
}
```

### 2. Chapter.vue 优化

**当前问题：**
- 串行API请求（慢）
- Markdown渲染无防抖（卡顿）
- 无加载状态提示

**优化方案：**

**并行化请求：**
```typescript
// 优化前（串行）
const loadChapter = async () => {
  const desk = await chapterApi.getDesk(slug.value, chapterId.value)
  const body = await chapterApi.getBody(slug.value, chapterId.value)
  const review = await chapterApi.getReview(slug.value, chapterId.value)
  const summary = await chapterApi.getSummary(slug.value, chapterId.value)
}

// 优化后（并行）
const loadChapter = async () => {
  const [desk, body, review, summary] = await Promise.all([
    chapterApi.getDesk(slug.value, chapterId.value),
    chapterApi.getBody(slug.value, chapterId.value),
    chapterApi.getReview(slug.value, chapterId.value),
    chapterApi.getSummary(slug.value, chapterId.value)
  ])
}
```

**Markdown防抖：**
```typescript
import { useDebounceFn } from '@vueuse/core'

const content = ref('')
const renderedContent = ref('')

const renderMarkdown = useDebounceFn((text: string) => {
  renderedContent.value = marked(text)
}, 300)

watch(content, (newContent) => {
  renderMarkdown(newContent)
})
```

**加载状态：**
```vue
<template>
  <div class="chapter">
    <n-spin :show="loading">
      <div v-if="!loading" class="chapter-content">
        <!-- 内容 -->
      </div>
      <template #description>
        <n-skeleton v-if="loading" text :repeat="10" />
      </template>
    </n-spin>
  </div>
</template>
```

### 3. vis-network 迁移

**迁移清单：**

1. **Cast.vue** - 人物关系图
   - 替换 `<Network>` 为 `<v-chart>`
   - 转换数据格式：vis nodes/edges → ECharts graph data
   - 保留交互功能（点击、拖拽、缩放）

2. **CastGraphCompact.vue** - 简化版关系图
   - 同上，但使用更小的节点和更简单的布局

3. **KnowledgeTripleGraph.vue** - 知识三元组图
   - 转换三元组为图数据
   - 使用ECharts Graph的分类功能区分实体类型

**迁移步骤：**

```typescript
// 1. 数据转换函数
function convertVisToECharts(visData: VisData): GraphData {
  return {
    nodes: visData.nodes.map(node => ({
      id: node.id,
      name: node.label,
      category: node.group
    })),
    edges: visData.edges.map(edge => ({
      source: edge.from,
      target: edge.to,
      value: edge.value || 1
    }))
  }
}

// 2. 替换组件
// 优化前
<Network :nodes="nodes" :edges="edges" :options="options" />

// 优化后
<GraphChart :data="graphData" :loading="loading" />
```

**删除依赖：**
```bash
npm uninstall vis-network
```

**删除文件：**
- 删除 `web-app/src/components/Cast.vue` 中的vis-network相关代码
- 删除 `web-app/src/components/CastGraphCompact.vue` 中的vis-network相关代码
- 删除 `web-app/src/components/KnowledgeTripleGraph.vue` 中的vis-network相关代码

---

## 实施计划

### Day 8-9: UI组件实现

**Day 8：基础组件**
- [ ] 创建 `StatCard.vue`（通用统计卡片）
- [ ] 创建 `StatsSidebar.vue`（主页侧边栏）
- [ ] 集成到 `Home.vue`
- [ ] 测试响应式布局

**Day 9：工作台组件**
- [ ] 创建 `StatsTopBar.vue`（工作台顶部条）
- [ ] 创建 `JobStatusIndicator.vue`（AI任务状态）
- [ ] 集成到 `Workbench.vue`
- [ ] 实现任务状态轮询

### Day 10-11: 图表组件

**Day 10：基础图表**
- [ ] 创建 `ProgressChart.vue`（进度条形图）
- [ ] 创建 `TrendChart.vue`（趋势折线图）
- [ ] 创建 `DistributionChart.vue`（分布饼图）
- [ ] 测试图表渲染和交互

**Day 11：关系图**
- [ ] 创建 `GraphChart.vue`（ECharts Graph）
- [ ] 实现力导向布局
- [ ] 测试节点交互（点击、拖拽、缩放）

### Day 12-13: vis-network迁移

**Day 12：Cast组件迁移**
- [ ] 替换 `Cast.vue` 中的vis-network
- [ ] 替换 `CastGraphCompact.vue` 中的vis-network
- [ ] 测试功能一致性

**Day 13：知识图谱迁移**
- [ ] 替换 `KnowledgeTripleGraph.vue` 中的vis-network
- [ ] 删除vis-network依赖
- [ ] 全面测试所有图表

### Day 14: 代码重构

**Workbench.vue拆分**
- [ ] 创建 `ChapterList.vue`
- [ ] 创建 `ChatArea.vue`
- [ ] 创建 `SettingsPanel.vue`
- [ ] 创建 `composables/useWorkbench.ts`
- [ ] 重构 `Workbench.vue`
- [ ] 删除旧代码

**Chapter.vue优化**
- [ ] 并行化API请求
- [ ] 添加Markdown防抖
- [ ] 添加加载状态

**统计刷新集成**
- [ ] 扩展 `statsStore.ts`（onJobCompleted, onChapterSaved）
- [ ] 集成到 `JobStatusIndicator.vue`
- [ ] 集成到 `Chapter.vue`
- [ ] 测试缓存失效

---

## 技术细节

### 1. 样式规范

**颜色系统：**
```css
/* 主色调 */
--primary: #3b82f6;
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #8b5cf6;

/* 灰度 */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-500: #6b7280;
--gray-700: #374151;
--gray-900: #111827;

/* 渐变 */
--gradient-blue: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-green: linear-gradient(135deg, #10b981 0%, #059669 100%);
```

**间距系统：**
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

**圆角：**
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-full: 9999px;
```

### 2. 响应式断点

```css
/* 桌面端 */
@media (min-width: 1200px) {
  .stats-sidebar { display: block; }
  .stats-top-bar { flex-direction: row; }
}

/* 平板端 */
@media (min-width: 768px) and (max-width: 1199px) {
  .stats-sidebar { width: 240px; }
  .stats-top-bar { flex-wrap: wrap; }
}

/* 移动端（暂不支持） */
@media (max-width: 767px) {
  .stats-sidebar { display: none; }
}
```

### 3. 错误处理

**API错误处理：**
```typescript
try {
  const data = await statsApi.getGlobal()
  return data
} catch (error) {
  console.error('Failed to load global stats:', error)
  window.$message.error('加载统计数据失败，请稍后重试')
  return null
}
```

**任务轮询错误处理：**
```typescript
const pollJobStatus = async () => {
  try {
    const status = await jobApi.getStatus(props.jobId)
    jobStatus.value = status

    if (status.done) {
      stopPolling()
      if (status.status === 'error') {
        window.$message.error(`任务失败：${status.error}`)
      } else {
        window.$message.success('任务完成！')
      }
      emit('completed', status)
    }
  } catch (error) {
    console.error('Failed to poll job status:', error)
    // 继续轮询，不中断
  }
}
```

### 4. 性能优化

**图表懒加载：**
```typescript
import { defineAsyncComponent } from 'vue'

const ProgressChart = defineAsyncComponent(() =>
  import('@/components/charts/ProgressChart.vue')
)
```

**防抖渲染：**
```typescript
import { useDebounceFn } from '@vueuse/core'

const debouncedRender = useDebounceFn(() => {
  // 渲染逻辑
}, 300)
```

**并行请求：**
```typescript
const [data1, data2, data3] = await Promise.all([
  api1(),
  api2(),
  api3()
])
```

### 5. 测试策略

**组件测试：**
- StatCard: 测试props渲染、加载状态、趋势显示
- JobStatusIndicator: 测试轮询逻辑、取消功能、完成事件
- GraphChart: 测试数据转换、交互功能

**集成测试：**
- 主页侧边栏：测试数据加载、刷新功能
- 工作台顶部条：测试任务状态显示、统计更新
- 图表组件：测试数据绑定、响应式更新

**端到端测试：**
- 启动AI任务 → 显示状态指示器 → 任务完成 → 统计刷新
- 保存章节 → 统计更新 → 图表重新渲染

---

## 总结

### 完成标准

**功能完整性：**
- ✅ 主页侧边栏显示全局统计
- ✅ 工作台顶部条显示书籍统计和AI任务状态
- ✅ 4个图表组件正常渲染和交互
- ✅ vis-network完全替换为ECharts
- ✅ Workbench.vue拆分为4个子组件
- ✅ Chapter.vue性能优化完成
- ✅ AI任务状态实时追踪
- ✅ 统计数据自动刷新

**代码质量：**
- ✅ 所有组件 < 200行
- ✅ 类型安全（无any）
- ✅ 无重复代码
- ✅ 清晰的文件结构
- ✅ 旧代码已删除

**用户体验：**
- ✅ 加载状态提示
- ✅ 错误处理和重试
- ✅ 响应式布局
- ✅ 流畅的交互

### 后续扩展

**第三阶段（可选）：**
- AI使用统计（Token消耗、成本估算）
- 项目健康度分析（一致性检查、冲突检测）
- 多书籍对比（跨项目统计、效率对比）
- 高级图表（事件时间线、场景地图）

---

**文档结束**