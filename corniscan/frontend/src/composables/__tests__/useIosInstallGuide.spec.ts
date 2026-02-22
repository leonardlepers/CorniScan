/**
 * Tests Story 6.3 — useIosInstallGuide composable
 *
 * AC#1 : guide affiché sur iOS Safari non standalone, premier login
 * AC#3 : ne s'affiche plus après dismissGuide (localStorage)
 * AC#4 : non affiché sur non-iOS / non-Safari / standalone
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useIosInstallGuide } from '@/composables/useIosInstallGuide'

const IOS_SAFARI_UA =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
const ANDROID_CHROME_UA =
  'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36'
const IOS_CHROME_UA =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/118.0.0.0 Mobile/15E148 Safari/604.1'

// ── localStorage mock (jsdom 28 ne garantit pas tous les méthodes) ───────────
let lsStore: Record<string, string> = {}
const localStorageMock = {
  getItem: (key: string) => lsStore[key] ?? null,
  setItem: (key: string, value: string) => { lsStore[key] = value },
  removeItem: (key: string) => { delete lsStore[key] },
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function mockUserAgent(ua: string) {
  vi.spyOn(navigator, 'userAgent', 'get').mockReturnValue(ua)
}

function mockStandalone(value: boolean) {
  // matchMedia n'est pas implémenté dans jsdom — on le stub via vi.stubGlobal
  vi.stubGlobal('matchMedia', () => ({ matches: value }))
}

// ── Setup ─────────────────────────────────────────────────────────────────────
describe('useIosInstallGuide', () => {
  beforeEach(() => {
    lsStore = {}
    vi.stubGlobal('localStorage', localStorageMock)
    // matchMedia par défaut → non standalone
    vi.stubGlobal('matchMedia', () => ({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  // AC#1 — guide affiché sur iOS Safari non standalone, jamais vu
  it('showGuide = true sur iOS Safari non standalone au premier login', () => {
    mockUserAgent(IOS_SAFARI_UA)
    mockStandalone(false)
    const { showGuide, checkAndShow } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(true)
  })

  // AC#4 — non-iOS
  it('showGuide = false sur Android Chrome', () => {
    mockUserAgent(ANDROID_CHROME_UA)
    mockStandalone(false)
    const { showGuide, checkAndShow } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(false)
  })

  // AC#4 — iOS mais Chrome (CriOS)
  it('showGuide = false sur iOS Chrome (CriOS)', () => {
    mockUserAgent(IOS_CHROME_UA)
    mockStandalone(false)
    const { showGuide, checkAndShow } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(false)
  })

  // AC#4 — déjà standalone
  it('showGuide = false si déjà en mode standalone', () => {
    mockUserAgent(IOS_SAFARI_UA)
    mockStandalone(true)
    const { showGuide, checkAndShow } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(false)
  })

  // AC#3 — ne s'affiche plus si guide déjà vu
  it('showGuide = false si guide déjà vu (localStorage)', () => {
    lsStore['ios_install_guide_shown'] = 'true'
    mockUserAgent(IOS_SAFARI_UA)
    mockStandalone(false)
    const { showGuide, checkAndShow } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(false)
  })

  // AC#3 — dismissGuide ferme le guide et persiste dans localStorage
  it('dismissGuide remet showGuide à false et écrit dans localStorage', () => {
    mockUserAgent(IOS_SAFARI_UA)
    mockStandalone(false)
    const { showGuide, checkAndShow, dismissGuide } = useIosInstallGuide()
    checkAndShow()
    expect(showGuide.value).toBe(true)

    dismissGuide()
    expect(showGuide.value).toBe(false)
    expect(lsStore['ios_install_guide_shown']).toBe('true')
  })

  // AC#3 — après dismiss, checkAndShow ne réaffiche plus le guide
  it('ne réaffiche pas le guide après dismiss', () => {
    mockUserAgent(IOS_SAFARI_UA)
    mockStandalone(false)
    const { checkAndShow, dismissGuide } = useIosInstallGuide()
    checkAndShow()
    dismissGuide()

    // Simuler un second login (nouvelle instance du composable, même lsStore)
    const { showGuide: showGuide2, checkAndShow: checkAndShow2 } = useIosInstallGuide()
    checkAndShow2()
    expect(showGuide2.value).toBe(false)
  })
})
