<template>
  <div class="login-page" :class="{ 'login-page-simple': needSimpleMode }">
    <!-- Animated background particles (mobile/Windows: 4, desktop: 20) -->
    <div class="bg-particles">
      <span v-for="i in particleCount" :key="i" class="particle" :class="{ 'particle-simple': needSimpleMode }" :style="particleStyle(i)"></span>
    </div>

    <div class="login-card" :class="{ 'login-card-simple': needSimpleMode }">
      <div class="login-logo">
        <img src="/yunji-logo.png" alt="云迹" class="logo-img" :class="{ 'logo-img-static': needSimpleMode }" />
      </div>
      <h1 class="login-title">云迹</h1>
      <p class="login-subtitle">哲法er交流学习平台</p>

      <div class="form-group">
        <label class="form-label">用户名或邮箱</label>
        <input class="form-input" v-model="username" placeholder="用户名，或已绑定邮箱登录" @keyup.enter="handleLogin" />
      </div>
      <div class="form-group">
        <label class="form-label">密码</label>
        <input class="form-input" type="password" v-model="password" placeholder="输入密码" @keyup.enter="handleLogin" />
      </div>

      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

      <button class="btn btn-primary btn-block" :disabled="loading || !hasAgreed" @click="handleLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <!-- User Agreement -->
      <button class="notice-btn" @click="showNotice = true">
        <span class="notice-icon">📋</span> 用户使用须知
      </button>
      <p v-if="!hasAgreed" class="agree-hint">请先阅读并同意《用户使用须知》后方可登录</p>

      <p class="forgot-row">
        <router-link to="/forgot-password" class="link">忘记密码？</router-link>
      </p>
      <p class="switch-text">
        没有账号？<router-link to="/register" class="link">立即注册</router-link>
      </p>

    </div>

    <!-- Notice Modal -->
    <Teleport to="body">
      <div v-if="showNotice" class="modal-overlay" @click.self="onOverlayClick">
        <div class="modal-box">
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
              <li>危害国家安全，反对宪法基本原则，损害国家荣誉与利益，歪曲历史、诋毁英烈，涉及非法组织、邪教、封建迷信的信息。</li>
              <li>色情低俗、淫秽露骨、性暗示、低俗交友、诱导私密联系等违背公序良俗的内容。</li>
              <li>宣扬暴力、血腥、自残、虐待，教唆赌博、诈骗、代考、作弊、翻墙、黑产等违法违规行为的信息。</li>
              <li>未经许可的商业广告、微商推广、电商引流、兼职刷单、付费资料、代写代考、校园贷等营销及盈利性信息。</li>
              <li>盗用、抄袭、盗版他人作品，擅自泄露他人姓名、联系方式、宿舍地址、照片、聊天记录等隐私信息。</li>
              <li>人身攻击、辱骂诽谤、恶意挂人、网络暴力、地域歧视、引战对立、煽动矛盾的言论。</li>
              <li>虚假通知、不实谣言、恶意造谣、误导性信息，冒充学校或官方机构发布的虚假内容。</li>
              <li>重复刷屏、无意义灌水、恶意霸屏、批量发布垃圾内容，干扰平台正常交流秩序的行为。</li>
              <li>其他违反法律法规、违背公序良俗、侵害他人合法权益、影响平台安全稳定的内容。</li>
            </ol>

            <h4>三、用户权利与义务</h4>
            <ol>
              <li>用户有权在合规范围内发布学习心得、个人成果、经验分享、合理求助等合法内容。</li>
              <li>用户有权对违规信息进行举报，平台将及时核查处理。</li>
              <li>用户有义务配合平台管理，对违规行为及时整改，不得抗拒、阻挠正常管理工作。</li>
              <li>用户应自行对账号安全、发布内容负责，因个人行为产生的法律责任由本人承担。</li>
            </ol>

            <h4>四、违规处理规则</h4>
            <ol>
              <li>平台发现违规信息，将视情节采取提醒警告、内容删除、禁言、临时限制功能、永久封禁账号等处理措施。</li>
              <li>多次违规、情节严重或造成不良影响的，将永久封禁账号并保留记录。</li>
              <li>涉嫌违法犯罪的，平台将依法上报相关部门并配合调查，追究相应法律责任。</li>
            </ol>

            <h4>五、其他说明</h4>
            <ol>
              <li>本平台为非盈利、公益性质学习交流工具，不向用户收取任何服务费用。</li>
              <li>平台将依法保护用户个人信息与隐私安全，不随意泄露用户数据。</li>
              <li>平台可根据运营需要、监管要求，适时修订本须知，修订后将同步更新，用户继续使用视为同意更新后的条款。</li>
              <li>本须知最终解释权归开发者所有，如有疑问可通过平台反馈渠道联系处理。</li>
            </ol>

            <p class="notice-footer-text">使用即表示已阅读、理解并同意遵守本须知全部条款，请文明交流、合规使用。</p>
          </div>
          <div class="modal-footer">
            <p v-if="!hasScrolledToBottom" class="scroll-hint">请阅读至底部后方可同意</p>
            <button class="btn btn-primary btn-block" :disabled="!hasScrolledToBottom" @click="onAgree">
              {{ hasScrolledToBottom ? '我已阅读并同意' : '请阅读完整须知...' }}
            </button>
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

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

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
  const opacity = 0.15 + Math.random() * 0.35
  return {
    width: size + 'px', height: size + 'px',
    left: left + '%',
    animationDelay: delay + 's',
    animationDuration: duration + 's',
    opacity
  }
}

function onNoticeScroll() {
  if (!noticeBody.value || hasScrolledToBottom.value) return
  const el = noticeBody.value
  const threshold = 30
  if (el.scrollHeight - el.scrollTop - el.clientHeight < threshold) {
    hasScrolledToBottom.value = true
  }
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
  if (hasAgreed.value) {
    showNotice.value = false
  } else {
    showToast('请先阅读并同意使用须知')
  }
}

async function handleLogin() {
  if (!hasAgreed.value) { showToast('请先阅读并同意《用户使用须知》'); return }
  if (!username.value.trim()) { errorMsg.value = '请输入用户名或邮箱'; return }
  if (!password.value) { errorMsg.value = '请输入密码'; return }
  loading.value = true
  errorMsg.value = ''
  try {
    const user = await login(username.value.trim(), password.value)
    showToast('登录成功')
    await nextTick()
    const target = user.profileCompleted ? '/feed' : '/profile-edit'
    await router.replace(target)
  } catch (e) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  padding: 16px; position: relative; overflow: hidden;
  background: linear-gradient(-45deg, #e8d5b7, #f5e6d3, #d4e7d0, #c8dbe8, #e0cce8);
  background-size: 400% 400%;
  animation: bgShift 18s ease infinite;
}
.login-page-simple {
  animation: none;
  background: linear-gradient(135deg, #e8d5b7 0%, #d4e7d0 50%, #c8dbe8 100%);
}

@keyframes bgShift {
  0%   { background-position: 0% 50%; }
  25%  { background-position: 100% 50%; }
  50%  { background-position: 100% 100%; }
  75%  { background-position: 0% 100%; }
  100% { background-position: 0% 50%; }
}

.bg-particles {
  position: absolute; inset: 0; pointer-events: none; z-index: 0;
}
.particle {
  position: absolute; bottom: -20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: floatUp linear infinite;
}
.particle:nth-child(odd) {
  background: rgba(168, 200, 140, 0.45);
}
.particle:nth-child(3n) {
  background: rgba(210, 180, 140, 0.4);
}

@keyframes floatUp {
  0%   { transform: translateY(0) scale(1); opacity: var(--o, 0.3); }
  50%  { opacity: var(--o, 0.3); }
  100% { transform: translateY(-110vh) scale(0.3); opacity: 0; }
}
.particle-simple {
  animation-duration: 12s;
}

.login-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-lg); padding: 40px 32px;
  width: 100%; max-width: 400px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255,255,255,0.6);
  text-align: center; position: relative; z-index: 1;
}
.login-card-simple {
  backdrop-filter: none;
  background: #fff;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
}
.login-logo {
  margin-bottom: 8px; display: flex; justify-content: center;
}
.logo-img {
  width: 100px; height: 100px; object-fit: contain;
  border-radius: 50%;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.12));
  animation: logoBounce 3s ease-in-out infinite;
}
.logo-img-static {
  animation: none;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));
}

@keyframes logoBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.login-title { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.login-subtitle { color: var(--text-secondary); margin-bottom: 32px; }
.error-text { color: var(--danger); font-size: 0.85rem; margin-bottom: 12px; }
.login-hint { margin-top: 20px; }

/* Notice Button */
.notice-btn {
  display: inline-flex; align-items: center; gap: 6px;
  margin-top: 14px; padding: 8px 18px;
  background: transparent; border: 1px solid var(--border);
  border-radius: 100px; font-size: 0.85rem;
  color: var(--primary); cursor: pointer;
  transition: var(--transition);
}
.notice-btn:hover { background: rgba(74,144,217,0.08); border-color: var(--primary); }
.notice-icon { font-size: 1rem; }
.agree-hint {
  margin-top: 8px; font-size: 0.78rem; color: var(--warning); font-weight: 500;
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(0, 0, 0, 0.5);
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-box {
  background: #fff; border-radius: 16px;
  width: 100%; max-width: 560px; max-height: 85vh;
  display: flex; flex-direction: column;
  box-shadow: 0 16px 64px rgba(0,0,0,0.2);
  animation: slideUp 0.3s ease;
}
@keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 16px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.modal-header h3 { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.modal-close {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--bg); font-size: 1.3rem; color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  transition: var(--transition);
}
.modal-close:hover { background: var(--border); color: var(--text-primary); }

.modal-body {
  flex: 1; overflow-y: auto; padding: 20px 24px;
  font-size: 0.88rem; line-height: 1.75; color: var(--text-primary);
}
.modal-body h4 {
  font-size: 0.95rem; font-weight: 700; color: var(--text-primary);
  margin-top: 20px; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 2px solid var(--primary);
  display: inline-block;
}
.modal-body ol {
  padding-left: 20px; margin-bottom: 12px;
}
.modal-body li {
  margin-bottom: 6px; list-style: decimal;
}
.notice-lead {
  margin-bottom: 16px; color: var(--text-secondary);
  padding: 12px 14px; background: #F8F9FA; border-radius: 8px;
  border-left: 3px solid var(--primary);
}
.notice-footer-text {
  margin-top: 20px; padding: 14px;
  background: #E8F5E9; border-radius: 8px;
  color: #2E7D32; font-weight: 600; text-align: center;
}

.modal-footer {
  padding: 16px 24px 20px; border-top: 1px solid var(--border); flex-shrink: 0;
}
.scroll-hint {
  text-align: center; font-size: 0.8rem; color: var(--warning);
  margin-bottom: 10px; font-weight: 500;
}

.forgot-row { margin-top: 12px; font-size: 0.85rem; text-align: center; }
/* Register link */
.switch-text { margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary); }
.link { color: var(--primary); font-weight: 600; }
.link:hover { text-decoration: underline; }
</style>
