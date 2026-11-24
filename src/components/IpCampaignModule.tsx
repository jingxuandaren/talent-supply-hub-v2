import {
  ArrowUpRight,
  CalendarDays,
  Gift,
  Sparkles,
  UsersRound,
} from 'lucide-react';
import autumnBeautyImage from '../assets/autumn-beauty.png';
import autumnEmotionsImage from '../assets/autumn-emotions.png';
import gameImage1 from '../assets/game-poster-1.jpg';
import gameImage2 from '../assets/game-poster-2.jpg';
import gameImage3 from '../assets/game-poster-3.jpg';
import gameImage4 from '../assets/game-poster-4.jpg';
import gameImage5 from '../assets/game-poster-5.jpg';
import gameImage6 from '../assets/game-poster-6.jpg';
import voyageAnswer from '../assets/ip-voyage-answer.jpg';

import homeImage from '../assets/XJtIMkuowNpPIBrpSYoEOSvSODiZFCvpEmvmlnxI.png';
import q4Image4 from '../assets/cmsLHnGlZkFuKWeFNgwRDAUiLqaAUPWIrLmtlvTT.png';
import q4Image2 from '../assets/fIhHpwuYeMgWphuTatktEfEsBjkuKbnBHzrJnprO.png';
import q4Image3 from '../assets/iLQXCkAlgyFnzmlaVgaPjBxFWqIRadlKJoDLmfBC.png';
import doubleHolidayPoster1 from '../assets/ip-double-holiday-poster-1.png';
import doubleHolidayPreview1 from '../assets/ip-double-holiday-poster-1.webp';
import doubleHolidayPoster2 from '../assets/ip-double-holiday-poster-2.png';
import doubleHolidayPreview2 from '../assets/ip-double-holiday-poster-2.webp';
import winterPoster1 from '../assets/ip-winter-beauty-1.png';
import winterPreview1 from '../assets/ip-winter-beauty-1.webp';
import winterPoster2 from '../assets/ip-winter-beauty-2.png';
import winterPreview2 from '../assets/ip-winter-beauty-2.webp';
import winterPoster3 from '../assets/ip-winter-beauty-3.png';
import winterPreview3 from '../assets/ip-winter-beauty-3.webp';
import winterPoster4 from '../assets/ip-winter-beauty-4.png';
import winterPreview4 from '../assets/ip-winter-beauty-4.webp';
import winterPoster5 from '../assets/ip-winter-beauty-5.png';
import winterPreview5 from '../assets/ip-winter-beauty-5.webp';
import q4Image1 from '../assets/kNYShsdOiBKkobykZECUHhOvZKZThNbwbdQMtzRT.png';

const CAMPAIGN_IMAGES: Record<string, string[]> = {
  '00': [doubleHolidayPoster1, doubleHolidayPoster2],
  '07': [
    winterPoster1,
    winterPoster2,
    winterPoster3,
    winterPoster4,
    winterPoster5,
  ],
  '02': [
    gameImage1,
    gameImage2,
    gameImage3,
    gameImage4,
    gameImage5,
    gameImage6,
  ],
  '03': [homeImage],
  '04': [q4Image1, q4Image2, q4Image3, q4Image4],
  '06': [voyageAnswer],
};

const CAMPAIGN_PREVIEWS: Record<string, string[]> = {
  '00': [doubleHolidayPreview1, doubleHolidayPreview2],
  '07': [
    winterPreview1,
    winterPreview2,
    winterPreview3,
    winterPreview4,
    winterPreview5,
  ],
};
const CAMPAIGN_IMAGE_SIZES: Record<string, [number, number][]> = {
  '00': [
    [3594, 1964],
    [1992, 1598],
  ],
  '07': [
    [957, 1280],
    [957, 1280],
    [1280, 720],
    [957, 1280],
    [1280, 720],
  ],
};

function CampaignGallery({ campaign }: { campaign: IpCampaign }) {
  const images = CAMPAIGN_IMAGES[campaign.index];
  if (!images) return null;
  return (
    <div
      id={`ip-gallery-${campaign.index}`}
      className={`ip-campaign-gallery ip-gallery-${campaign.index}`}
      aria-label={`${campaign.industry}企划展示图`}
    >
      {images.map((image, index) => (
        <a
          href={image}
          key={image}
          target="_blank"
          rel="noreferrer"
          aria-label={`查看${campaign.industry}合作企划第${index + 1}张原图`}
        >
          <img
            src={CAMPAIGN_PREVIEWS[campaign.index]?.[index] ?? image}
            width={CAMPAIGN_IMAGE_SIZES[campaign.index]?.[index]?.[0]}
            height={CAMPAIGN_IMAGE_SIZES[campaign.index]?.[index]?.[1]}
            loading="lazy"
            decoding="async"
            alt={`${campaign.industry}合作企划展示图 ${index + 1}`}
          />
        </a>
      ))}
    </div>
  );
}

type CampaignLink = {
  label: string;
  url: string;
  primary?: boolean;
};

type IpCampaign = {
  index: string;
  industry: string;
  title: string;
  period: string;
  quota: string;
  summary: string;
  benefits: string[];
  links: CampaignLink[];
  tone: string;
  feature?: boolean;
};

const CAMPAIGNS: IpCampaign[] = [
  {
    index: '00',
    industry: '全行业 · 双旦节点',
    title: '巨量星图「双旦奇遇派对」达人合作方案',
    period: '2026.11.16 — 2027.01.15',
    quota: '50万 / 100万 / 200万 / 500万',
    summary:
      '以节日创意、节日种草和专业测评三阶内容递进，覆盖蓄水、爆发与长尾阶段，承接双旦送礼、悦己和节日参与需求。',
    benefits: [
      '搜索 2.0、搜索 1.0 多词与共创组件',
      'H5 露出、PR 宣发与精选达人激励',
      '星选种草团 3% 赠款，电商联投 55% 反哺',
    ],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/docx/PPNgdqUmSoWWKXxBlv9cjCT1nOc?from=from_copylink',
        primary: true,
      },
    ],
    tone: 'rose',
    feature: true,
  },
  {
    index: '07',
    industry: '美妆行业 · 冰雪季',
    title: '2026美妆冰雪季「#赴一场冬日美约」星图直充活动',
    period: '2026.11.16 — 12.31',
    quota: '500万 / 300万 / 200万 / 100万 / 30万',
    summary:
      '聚焦冰雪出游、冬日妆容与严苛环境功效实测，以 OPBU 内容生态与精选达人矩阵，串联趋势引领、场景种草和转化承接。',
    benefits: [
      '搜索组件 2.0 / 1.0 多词与共创组件（按档位适用）',
      '精选达人合作企划与限时服务费抵扣激励',
      '冰雪季特色达人供给与冬日美妆场景种草',
    ],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/docx/IuxRdKfbYo2EfHxKVYucahuwnjh?from=from_copylink',
        primary: true,
      },
    ],
    tone: 'winter',
    feature: true,
  },
  {
    index: '01',
    industry: '日化行业',
    title: '巨量星图✖️日化行业「入秋情绪图鉴」直充活动',
    period: '2026.09.01 — 10.15',
    quota: '500万 / 200万 / 100万 / 30万',
    summary: '从发丝到指尖，用四大入秋情绪人群图鉴连接品牌与消费者的秋日情绪。',
    benefits: [
      '精选达人服务费抵扣',
      '搜索组件 2.0 / 1.0',
      '电商联投与流量激励',
    ],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/wiki/UA8Bwp5yniC0eFkfUHdcBp5anAm?from=from_copylink',
        primary: true,
      },
    ],
    tone: 'amber',
  },
  {
    index: '02',
    industry: '游戏行业',
    title: '巨量星图｜Q3游戏「精选达人」合作企划案',
    period: '2026.08.27 — 09.30',
    quota: '报名行业：中国广告销售平台-直客业务-互动娱乐',
    summary:
      '以优质内容承接破圈、种草与转化，帮助游戏厂商把营销话术变成玩家愿意看的内容。',
    benefits: ['精选达人服务费抵扣', '六类特色营销官', '完整达人刊例'],
    links: [
      {
        label: '查看企划案',
        url: 'https://bytedance.larkoffice.com/docx/Tl6bdDg6eoBAbTxJTdNcCWmen2b?from=from_copylink',
        primary: true,
      },
      {
        label: '达人刊例',
        url: 'https://bytedance.larkoffice.com/sheets/G8A9s1saShCTJpt6ACFcJRYqnxe?sheet=b54148',
      },
    ],
    tone: 'violet',
  },
  {
    index: '03',
    industry: '家居行业',
    title: '巨量星图家居行业「Star 超会装 家的秋季灵感」活动方案',
    period: '2026.09.01 — 11.15',
    quota: '500万 / 200万 / 50万',
    summary:
      '聚焦家装改造、家纺焕新与日用百货三大秋季消费场景，串联种草到进店转化。',
    benefits: ['精选达人合作企划', '流量与服务费激励', '秋季场景达人清单'],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/docx/H1nzdr08PonANixmF22cw8KRnZe?from=from_copylink',
        primary: true,
      },
      {
        label: '合作文档',
        url: 'https://bytedance.larkoffice.com/wiki/PtCVwjle8iLrREkLS4uc6Errncf',
      },
      {
        label: '推荐达人',
        url: 'https://bytedance.larkoffice.com/sheets/KvKtsmZIJhsn6rtHXvJcy6eln1E?from=from_copylink&sheet=83d343',
      },
    ],
    tone: 'copper',
  },
  {
    index: '04',
    industry: '婴宠行业',
    title: '【巨量星图】婴宠26年Q4内容洞察&激励活动',
    period: '2026.10.01 — 12.31',
    quota: '500万 / 200万 / 50万',
    summary:
      '围绕换季、大促、出行与年终陪伴场景，以内容策略和星图激励提升种草确定性。',
    benefits: [
      '限定客户：中国广告销售平台-直客业务-时尚婴宠-C组/D组/E组',
      '四大精选内容场景',
      'OA 锁席报名',
    ],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/wiki/GDwlwsXZyicAwikEmjocrEvwnfh?from=from_copylink',
        primary: true,
      },
      {
        label: '场景达人推荐',
        url: 'https://bytedance.larkoffice.com/wiki/LmzuwIPHsijgNbkbdhlcAZrmnDd',
      },
    ],
    tone: 'mint',
  },
  {
    index: '05',
    industry: '美妆行业',
    title: '巨量星图美妆行业「秋日好状态加载中」活动方案',
    period: '2026.09.11 — 10.25',
    quota: '500万 / 200万 / 100万 / 50万',
    summary:
      '围绕换季敏感、秋冬保湿、中式妆容与出游持妆，构建秋日好状态种草图鉴。',
    benefits: ['服务费抵扣与流量激励', '搜索组件多词权益', '电商联投达人配赠'],
    links: [
      {
        label: '查看活动方案',
        url: 'https://bytedance.larkoffice.com/wiki/TBXuwynSuioNnGkcZXVceoFnnrd?from=from_copylink',
        primary: true,
      },
    ],
    tone: 'rose',
  },
  {
    index: '06',
    industry: '教育行业 · 全行业开放',
    title: '【行业IP】远航计划-年终闪光答案季',
    period: '售卖 2026.11.01—12.31；上线 2026.12.20—2027.02.28',
    quota: '500万×1席 / 200万×2席 / 100万×3席 / 50万×3席',
    summary:
      '教育行业年终与寒假特别企划，以《年终答卷》串联人物对谈、知识竞技、达人共创与趋势话题，让每一个努力成长的人都被看见、被照亮。',
    benefits: [
      '官方主话题与 H5 品牌馆露出',
      '年终答卷植入、年终对谈与知识竞技（依合作档位）',
      '精选达人共创与流量激励机会；具体权益以最终资源包为准',
    ],
    links: [
      {
        label: '查看项目介绍与权益',
        url: 'https://bytedance.larkoffice.com/wiki/VE6Ow4GoOiOS2XkQFd1cgsGenff',
        primary: true,
      },
    ],
    tone: 'voyage',
  },
];

const CAMPAIGN_ORDER = ['00', '07', '05', '01', '03', '06', '02', '04'];

export function IpCampaignModule() {
  const preview =
    typeof window === 'undefined'
      ? null
      : new URLSearchParams(window.location.search).get('ipPreview');
  const campaigns =
    preview === 'beauty'
      ? CAMPAIGNS.filter(c => c.index === '05')
      : preview === 'first'
        ? CAMPAIGNS.filter(c => c.index === '01' || c.index === '02')
        : preview === 'home'
          ? CAMPAIGNS.filter(c => c.index === '03' || c.index === '06')
          : CAMPAIGN_ORDER.flatMap(index =>
              CAMPAIGNS.filter(c => c.index === index),
            );
  return (
    <section className="content-section enter ip-module">
      <div className="section-heading ip-heading">
        <div>
          <span className="eyebrow">CURATED · IP CAMPAIGNS</span>
          <h2>IP 精选合作企划</h2>
          <p>汇总重点行业内容 IP、直充活动与精选达人合作入口。</p>
        </div>
        <div className="ip-summary">
          <Sparkles size={18} />
          <span>{CAMPAIGNS.length} 个精选企划</span>
          <b>2026 双旦 · 秋冬档</b>
        </div>
      </div>
      <div className="ip-grid">
        {campaigns.map(campaign => (
          <article
            className={`ip-card ${campaign.tone}${campaign.index === '02' ? ' ip-game-card' : ''}${campaign.feature ? ' ip-feature-card' : ''}`}
            key={campaign.index}
          >
            <div className="ip-card-head">
              <span className="ip-industry">{campaign.industry}</span>
            </div>
            <h3>{campaign.title}</h3>
            {(campaign.index === '01' || campaign.index === '05') && (
              <a
                href={
                  campaign.index === '01'
                    ? autumnEmotionsImage
                    : autumnBeautyImage
                }
                target="_blank"
                rel="noreferrer"
                aria-label={`查看${campaign.title}完整展示图`}
              >
                <img
                  src={
                    campaign.index === '01'
                      ? autumnEmotionsImage
                      : autumnBeautyImage
                  }
                  alt={`${campaign.industry}${campaign.title}活动展示图`}
                  className="ip-hero-image"
                />
              </a>
            )}
            <p className="ip-summary-copy">{campaign.summary}</p>
            <div className="ip-facts">
              <div>
                <CalendarDays size={16} />
                <span>
                  <small>活动周期</small>
                  <b>{campaign.period}</b>
                </span>
              </div>
              <div>
                <UsersRound size={16} />
                <span>
                  <small>席位 / 范围</small>
                  <b>{campaign.quota}</b>
                </span>
              </div>
            </div>
            <div className="ip-benefits">
              <span>
                <Gift size={15} /> 核心权益
              </span>
              <ul>
                {campaign.benefits.map(benefit => (
                  <li key={benefit}>{benefit}</li>
                ))}
              </ul>
            </div>
            <CampaignGallery campaign={campaign} />
            <div className="ip-links">
              {campaign.links.map(link => (
                <a
                  className={link.primary ? 'primary' : ''}
                  href={link.url}
                  key={link.label}
                  target="_blank"
                  rel="noreferrer"
                >
                  {link.label} <ArrowUpRight size={13} />
                </a>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
