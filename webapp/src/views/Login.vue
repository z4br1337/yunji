<template>
  <div class="login-page" :class="{ 'login-page-simple': needSimpleMode }">
    <div class="backdrop backdrop-1"></div>
    <div class="backdrop backdrop-2"></div>
    <div class="backdrop backdrop-3"></div>
    <div class="bg-particles" aria-hidden="true">
      <span v-for="i in particleCount" :key="i" class="particle" :class="{ 'particle-simple': needSimpleMode }" :style="particleStyle(i)"></span>
      <div v-for="b in bgBlocks" :key="b.text + b.delay" class="bg-block" :class="b.className" :style="blockStyle(b)">
        <div class="bg-block-title">{{ b.text }}</div>
        <div class="bg-block-sub">{{ b.sub }}</div>
      </div>
    </div>
    <div class="login-shell">
      <div class="hero-illustration" aria-hidden="true">
        <div class="hero-glow hero-glow-1"></div>
        <div class="hero-glow hero-glow-2"></div>
        <div class="hero-glow hero-glow-3"></div>
        <img src="/yunji-logo.jpg" alt="" class="hero-avatar" />
      </div>
      <div class="login-card" :class="{ 'login-card-simple': needSimpleMode }">
        <div class="brand-head">
          <h1 class="login-title">云迹</h1>
          <p class="login-subtitle">哲法er交流学习平台</p>
        </div>

        <div class="form-group compact">
          <label class="form-label">用户名或学号</label>
          <input ref="usernameInput" class="form-input" v-model="username" placeholder="使用用户名或学号登录" @keyup.enter="onLoginClick" />
        </div>
        <div class="form-group compact">
          <label class="form-label">密码</label>
          <input class="form-input" type="password" v-model="password" placeholder="输入密码" @keyup.enter="onLoginClick" />
        </div>

        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

        <button class="btn btn-primary btn-block login-main-btn" :disabled="loading || !hasAgreed" @click="onLoginClick">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <button class="notice-btn" @click="showNotice = true">用户使用须知</button>
        <p v-if="!hasAgreed" class="agree-hint">请先阅读并同意《用户使用须知》后方可登录</p>

        <p class="switch-text">
          没有账号？<router-link to="/register" class="link">立即注册</router-link>
        </p>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="pickAccounts.length" class="modal-overlay" @click.self="pickAccounts = []">
        <div class="modal-box pick-modal">
          <h3 class="pick-title">选择要登录的账号</h3>
          <p class="text-sm text-secondary mb-12">该学号绑定了多个账号，请选择其一后继续。</p>
          <button v-for="acc in pickAccounts" :key="acc.username" type="button" class="pick-row" @click="loginAsAccount(acc.username)">
            <img v-if="acc.avatarUrl" class="pick-av" :src="acc.avatarUrl" alt="" />
            <div v-else class="pick-av pick-av-fallback">{{ (acc.nickname || '?')[0] }}</div>
            <div class="pick-meta">
              <span class="pick-name">{{ acc.nickname }}</span>
              <span class="pick-sub">@{{ acc.username }}</span>
            </div>
          </button>
          <button type="button" class="btn btn-ghost btn-block mt-12" @click="pickAccounts = []">取消</button>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showNotice" class="modal-overlay" @click.self="onOverlayClick">
        <div class="modal-box notice-modal">
          <div class="modal-header">
            <h3>云迹-CloudPebble 用户使用须知</h3>
            <button class="modal-close" @click="onCloseNotice">&times;</button>
          </div>
          <div class="modal-body" ref="noticeBody" @scroll="onNoticeScroll">
            <p class="notice-lead">本平台为个人开发、面向在校大学生的非盈利学习交流平台，专注提供学习经验交流、学生成果展示、新老生经验分享等正向服务。为保障社区文明、安全、合规运行，维护健康有序的交流环境，所有用户在注册、登录及使用过程中，均应认真阅读并严格遵守本须知。</p>
            <h4>一、基本使用准则</h4>
            <ol>
              <li>本平台仅用于在校大学生学习交流、经验分享、成果展示，禁止用于任何商业、盈利及违规用途。</li>
              <li>用户应保证注册信息真实、有效，不得冒用他人身份、伪造校园相关信息。</li>
              <li>使用过程中应尊重他人、理性发言、友善互动，共同维护纯净、正向的校园交流氛围。</li>
              <li>自觉遵守国家法律法规、平台规范及校园公序良俗，不发布、不传播任何违规、有害信息。</li>
            </ol>
            <h4>二、禁止发布与传播的内容</h4>
            <p>用户不得利用平台制作、上传、复制、传播以下内容：</p>
            <ol>
              <li>危害国家安全、违法违规、色情低俗、暴力血腥、诈骗引流、隐私泄露、网络暴力等信息。</li>
              <li>未经许可的商业广告、兼职刷单、代写代考、校园贷、付费资料等营销内容。</li>
              <li>虚假通知、不实谣言、恶意霸屏、重复刷屏及其他破坏平台秩序的行为。</li>
            </ol>
            <p class="notice-footer-text">使用即表示已阅读、理解并同意遵守本须知全部条款，请文明交流、合规使用。</p>
          </div>
          <div class="modal-footer">
            <p v-if="!hasScrolledToBottom" class="scroll-hint">请阅读至底部后方可同意</p>
            <button class="btn btn-primary btn-block" :disabled="!hasScrolledToBottom" @click="onAgree">{{ hasScrolledToBottom ? '我已阅读并同意' : '请阅读完整须知...' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, inject, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const { login } = useUserStore()
const showToast = inject('showToast')
const isWindows = inject('isWindows', ref(false))
const isMobile = inject('isMobile', ref(false))
const needSimpleMode = computed(() => isWindows.value || isMobile.value)
const particleCount = computed(() => (needSimpleMode.value ? 4 : 20))
const bgBlocks = [
  ['发帖很快', '灵感立刻开张'],
  ['匿名也稳', '表达更自在'],
  ['评论有梗', '互动更有趣'],
  ['私信秒回', '联系不掉线'],
  ['成果上墙', '高光随时秀'],
  ['积分拿捏', '兑换小惊喜'],
  ['活动追更', '校园不缺席'],
  ['广场热闹', '话题一直新'],
  ['消息不断', '陪伴不停歇'],
  ['成长发光', '记录每一天']
].map(([text, sub], index) => ({
  text,
  sub,
  delay: index * 0.03,
  duration: 30 + (index % 3) * 4,
  top: -2 + index * 3.0,
  left: -26 - index * 1.4,
  rotate: [-8, -5, -3, 2, 6][index % 5],
  size: [176, 204, 192, 216, 198][index % 5],
  className: index % 2 === 0 ? 'bg-block-warm' : 'bg-block-cool'
}))

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const pickAccounts = ref([])
const pendingPassword = ref('')
const usernameInput = ref(null)

const showNotice = ref(false)
const hasAgreed = ref(false)
const hasScrolledToBottom = ref(false)
const noticeBody = ref(null)

onMounted(() => {
  if (localStorage.getItem('yunji_agreed') === '1') {
    hasAgreed.value = true
  } else {
    showNotice.value = true
  }
})

function particleStyle(i) {
  const size = 4 + Math.random() * 12
  const left = Math.random() * 100
  const delay = Math.random() * 15
  const duration = 8 + Math.random() * 12
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

function blockStyle(b) {
  return {
    top: `${b.top}%`,
    left: `${b.left}%`,
    width: `${b.size}px`,
    animationDelay: `${b.delay}s`,
    animationDuration: `${b.duration}s`
  }
}

function onNoticeScroll() {
  if (!noticeBody.value || hasScrolledToBottom.value) return
  const el = noticeBody.value
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 30) hasScrolledToBottom.value = true
}

function onAgree() {
  hasAgreed.value = true
  showNotice.value = false
  localStorage.setItem('yunji_agreed', '1')
}

function onOverlayClick() {
  if (hasAgreed.value) showNotice.value = false
}

function onCloseNotice() {
  if (hasAgreed.value) showNotice.value = false
  else showToast('请先阅读并同意使用须知')
}

function userHasStudentId(u) {
  return !!(u && u.studentId && String(u.studentId).trim())
}

async function afterLoginSuccess(user) {
  showToast('登录成功')
  await nextTick()
  if (!userHasStudentId(user)) {
    await router.replace('/bind-student')
    return
  }
  await router.replace(user.profileCompleted ? '/feed' : '/profile-edit')
}

function onLoginClick() {
  pickAccounts.value = []
  pendingPassword.value = ''
  handleLogin()
}

async function loginAsAccount(selectedUsername) {
  const pwd = pendingPassword.value
  if (!pwd) return
  pickAccounts.value = []
  loading.value = true
  errorMsg.value = ''
  try {
    const user = await login(selectedUsername, pwd)
    await afterLoginSuccess(user)
  } catch (e) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
    pendingPassword.value = ''
  }
}

async function handleLogin() {
  if (!hasAgreed.value) { showToast('请先阅读并同意《用户使用须知》'); return }
  if (!username.value.trim()) { errorMsg.value = '请输入用户名或学号'; return }
  if (!password.value) { errorMsg.value = '请输入密码'; return }
  loading.value = true
  errorMsg.value = ''
  try {
    const result = await login(username.value.trim(), password.value)
    if (result && result.__pickAccount) {
      pendingPassword.value = password.value
      pickAccounts.value = result.accounts || []
      loading.value = false
      return
    }
    await afterLoginSuccess(result)
  } catch (e) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; padding: 18px; background: linear-gradient(180deg, #fff7ef 0%, #ffffff 46%, #fff7ef 100%); }
.login-page-simple { background: linear-gradient(180deg, #fff7ef 0%, #ffffff 50%, #fff7ef 100%); }
.backdrop { position: absolute; border-radius: 50%; filter: blur(22px); opacity: 0.8; pointer-events: none; }
.backdrop-1 { width: 280px; height: 280px; top: -50px; left: -70px; background: rgba(255,130,0,0.14); }
.backdrop-2 { width: 240px; height: 240px; top: 130px; right: -70px; background: rgba(47,128,237,0.10); }
.backdrop-3 { width: 260px; height: 260px; bottom: -80px; left: 18%; background: rgba(36,194,124,0.09); }
.bg-particles, .login-shell { position: relative; z-index: 1; }
.bg-particles { position: absolute; inset: 0; overflow: hidden; }
.particle { position: absolute; bottom: -20px; border-radius: 50%; background: rgba(255,255,255,0.55); animation: floatUp linear infinite; }
.particle:nth-child(odd) { background: rgba(255,130,0,0.08); }
.particle:nth-child(3n) { background: rgba(47,128,237,0.08); }
.bg-block {
  position: absolute;
  border-radius: 24px;
  padding: 20px 18px;
  backdrop-filter: blur(8px);
  box-shadow: 0 10px 24px rgba(255, 170, 170, 0.12);
  border: 1px solid rgba(255,255,255,0.58);
  animation-name: driftFade;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  animation-fill-mode: both;
  overflow: hidden;
  will-change: transform, opacity;
}
.bg-block::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.86), rgba(255,255,255,0.35));
  mask-image: radial-gradient(circle at 50% 50%, black 48%, transparent 100%);
}
.bg-block-title, .bg-block-sub { position: relative; z-index: 1; text-shadow: 0 1px 1px rgba(255,255,255,0.75); }
.bg-block-title { font-size: 1.02rem; font-weight: 800; margin-bottom: 6px; line-height: 1.1; }
.bg-block-sub { font-size: 0.78rem; font-weight: 600; opacity: 0.86; line-height: 1.1; }
.bg-block-warm { color: rgba(255, 101, 132, 0.72); background: rgba(255, 246, 249, 0.72); }
.bg-block-cool { color: rgba(101, 118, 255, 0.68); background: rgba(246, 248, 255, 0.72); }
.login-shell { width: 100%; max-width: 430px; position: relative; padding-top: 16px; }
.hero-illustration { position: relative; width: 100%; height: 230px; display: flex; align-items: center; justify-content: center; margin-bottom: 0; }
.hero-glow { position: absolute; border-radius: 50%; filter: blur(18px); opacity: 0.45; }
.hero-glow-1 { width: 210px; height: 210px; background: rgba(255, 205, 120, 0.28); top: 8px; left: 50%; transform: translateX(-50%); }
.hero-glow-2 { width: 160px; height: 160px; background: rgba(255, 140, 180, 0.16); top: 64px; left: calc(50% - 84px); }
.hero-glow-3 { width: 140px; height: 140px; background: rgba(140, 210, 150, 0.18); top: 78px; left: calc(50% + 64px); }
.hero-avatar { width: 172px; height: 172px; object-fit: contain; position: relative; z-index: 1; filter: drop-shadow(0 10px 24px rgba(0,0,0,0.08)); }
.login-card { margin-top: -18px; background: rgba(255,255,255,0.93); backdrop-filter: blur(14px); border-radius: 28px; padding: 24px 22px 28px; width: 100%; box-shadow: 0 18px 50px rgba(255,146,61,0.10); border: 1px solid rgba(255,255,255,0.85); text-align: center; position: relative; z-index: 2; }
.login-shell { width: 100%; max-width: 430px; }
.hero-illustration { position: relative; height: 250px; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; }
.hero-card, .hero-badge { position: absolute; border-radius: 24px; background: rgba(255,255,255,0.7); border: 1px solid rgba(255,255,255,0.6); }
.hero-card-1 { width: 210px; height: 130px; top: 10px; background: rgba(255,244,230,0.82); transform: rotate(-7deg); }
.hero-card-2 { width: 230px; height: 140px; top: 42px; background: rgba(233,249,244,0.9); transform: rotate(6deg); }
.hero-card-3 { width: 190px; height: 120px; top: 74px; background: rgba(245,238,255,0.85); transform: rotate(-2deg); }
.hero-badge-1 { width: 72px; height: 72px; top: 24px; right: 54px; background: rgba(255,255,255,0.95); }
.hero-badge-2 { width: 82px; height: 82px; bottom: 18px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.92); }
.login-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(14px); border-radius: 28px; padding: 24px 22px 28px; width: 100%; box-shadow: 0 18px 50px rgba(255,146,61,0.10); border: 1px solid rgba(255,255,255,0.85); text-align: center; }
.login-card-simple { backdrop-filter: none; background: #fff; }
.brand-head { display: flex; flex-direction: column; align-items: center; gap: 10px; margin-bottom: 18px; }
.logo-img { width: 92px; height: 92px; object-fit: contain; border-radius: 24px; box-shadow: 0 10px 28px rgba(0,0,0,0.08); }
.logo-img-static { animation: none; }
.login-title { font-size: 1.7rem; font-weight: 800; color: var(--text-primary); margin-bottom: 4px; }
.login-subtitle { color: var(--text-secondary); font-size: 0.95rem; }
.form-group.compact { margin-bottom: 12px; text-align: left; }
.form-group.compact .form-label { font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 6px; display: block; }
.form-group.compact .form-input { border-radius: 16px; background: #fafafa; border-color: #ececec; }
.login-main-btn { border-radius: 999px; margin-top: 8px; height: 48px; font-weight: 700; }
.error-text { color: var(--danger); font-size: 0.85rem; margin: 10px 0 8px; }
.notice-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; margin-top: 14px; padding: 8px 18px; background: transparent; border: none; border-radius: 999px; font-size: 0.85rem; color: var(--text-secondary); cursor: pointer; }
.notice-btn:hover { color: var(--primary); }
.notice-icon { display: none; }
.agree-hint { margin-top: 8px; font-size: 0.78rem; color: var(--warning); font-weight: 500; }
.modal-overlay { position: fixed; inset: 0; z-index: 10000; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 560px; max-height: 85vh; display: flex; flex-direction: column; box-shadow: 0 18px 64px rgba(0,0,0,0.18); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px 14px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
.modal-header h3 { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.modal-close { width: 32px; height: 32px; border-radius: 50%; background: var(--bg); font-size: 1.3rem; color: var(--text-muted); display: flex; align-items: center; justify-content: center; }
.modal-body { flex: 1; overflow-y: auto; padding: 18px 20px; font-size: 0.88rem; line-height: 1.7; color: var(--text-primary); }
.modal-body h4 { font-size: 0.95rem; font-weight: 700; margin-top: 16px; margin-bottom: 8px; }
.modal-body ol { padding-left: 18px; margin-bottom: 12px; }
.modal-body li { margin-bottom: 6px; }
.notice-lead { margin-bottom: 14px; color: var(--text-secondary); padding: 12px 14px; background: #fff8f2; border-radius: 12px; }
.notice-footer-text { margin-top: 18px; padding: 12px 14px; background: #fff4e8; border-radius: 12px; color: #c96b00; font-weight: 600; text-align: center; }
.modal-footer { padding: 16px 20px 20px; border-top: 1px solid var(--border); flex-shrink: 0; }
.scroll-hint { text-align: center; font-size: 0.8rem; color: var(--warning); margin-bottom: 10px; font-weight: 500; }
.pick-modal { padding: 20px 18px; max-width: 400px; }
.pick-title { font-size: 1.05rem; margin-bottom: 8px; }
.pick-row { display: flex; align-items: center; gap: 12px; width: 100%; padding: 12px; margin-bottom: 8px; border: 1px solid var(--border); border-radius: 14px; background: var(--bg-card); text-align: left; }
.pick-av { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.pick-av-fallback { display: flex; align-items: center; justify-content: center; background: var(--primary); color: #fff; font-weight: 700; }
.pick-meta { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.pick-name { font-weight: 600; }
.pick-sub { font-size: 0.8rem; color: var(--text-muted); }
.switch-text { margin-top: 16px; font-size: 0.85rem; color: var(--text-secondary); }
.link { color: var(--primary); font-weight: 600; }
@keyframes driftFade { 0% { transform: translate(-38vw, -16vh) rotate(-7deg); opacity: 0; } 12% { opacity: 1; } 85% { opacity: 1; } 100% { transform: translate(102vw, 4vh) rotate(-7deg); opacity: 0; } }
@keyframes floatUp { 0% { transform: translateY(0) scale(1); opacity: 0.18; } 50% { opacity: 0.18; } 100% { transform: translateY(-110vh) scale(0.3); opacity: 0; } }
@media (max-width: 480px) {
  .login-shell { max-width: 100%; padding-top: 16px; }
  .hero-illustration { height: 190px; }
  .hero-avatar { width: 138px; height: 138px; }
  .hero-glow-1 { width: 160px; height: 160px; }
  .hero-glow-2 { width: 126px; height: 126px; }
  .hero-glow-3 { width: 114px; height: 114px; }
  .login-card { margin-top: -12px; }
  .bg-block { padding: 14px 12px; border-radius: 20px; }
  .bg-block-title { font-size: 0.92rem; }
  .bg-block-sub { font-size: 0.7rem; }
}
</style>
