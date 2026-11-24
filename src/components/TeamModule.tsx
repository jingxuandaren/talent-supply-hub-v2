import { ArrowUpRight, BookOpen, UsersRound } from 'lucide-react';
import autoTeamHero from '../assets/team-auto-cover.png';
import goodsDecisionTeamHero from '../assets/team-goods-decision-cover.png';
import lifeDramaTeamHero from '../assets/team-life-drama-cover.jpg';
import newYearTeamHero from '../assets/team-newyear-cover.png';
import potentialTeamHero from '../assets/team-potential-cover.png';

type TeamSpec = {
  name: string;
  statusLabel: string;
  docUrl?: string;
  coverImage?: string;
  coverAlt?: string;
  docSummary?: {
    subtitle: string;
    bullets: string[];
  };
};

const TEAMS: TeamSpec[] = [
  {
    name: '2026巨量星图「人生百态剧情团」',
    statusLabel: 'NEW',
    docUrl: 'https://bytedance.larkoffice.com/wiki/IfzPwJ97UimaNkklxrlcxpxUn7d',
    coverImage: lifeDramaTeamHero,
    coverAlt: '2026巨量星图「人生百态剧情团」三大营销目标与特色达人团供给图',
    docSummary: {
      subtitle: '已发布资料：项目总览',
      bullets: [
        '营销目标：围绕大曝光、强种草、深转化，承接新品造势、场景种草和节点转化',
        '达人供给：汇聚真人演绎、AIGC 创意、生活叙事与好物推荐达人，候选池 2700+',
        '合作方式：曝光优先植入视频，场景种草优先定制视频，购买承接短直联动',
      ],
    },
  },
  {
    name: '2026巨量星图「年度好物决策团」',
    statusLabel: 'NEW',
    docUrl: 'https://bytedance.larkoffice.com/wiki/Lf02weC5fiUeQ9kPZabc7wl9nDb',
    coverImage: goodsDecisionTeamHero,
    coverAlt: '2026巨量星图「年度好物决策团」项目核心价值信息图',
    docSummary: {
      subtitle: '已发布资料：项目总览',
      bullets: [
        '营销节点：双十二、双旦跨年、CNY 年货节，聚焦年末至 2027 年初消费决策',
        '覆盖行业：美妆、3C 及电器、食品饮料、日化、家居建材',
        '内容供给：4 大特色子团 × 8 类内容玩法，支持一口价与短直联动',
      ],
    },
  },
  {
    name: '2026巨量星图「驭见星途·汽车达人团」',
    statusLabel: 'NEW',
    docUrl: 'https://bytedance.larkoffice.com/wiki/QsFuwyUM0ir9pykeJ8FcN5Vrnje',
    coverImage: autoTeamHero,
    coverAlt:
      '2026巨量星图「驭见星途·汽车达人团」飞书文档封面图：汽车达人团主视觉',
    docSummary: {
      subtitle: '已发布资料：项目总览',
      bullets: [
        '达人结构：专业汽车 / 女性视角 / 生活方式三类核心达人',
        '适配方向：新能源 / 燃油车 / 豪华车，并延展至旅行露营、宠物、亲子等生活方式场景',
        '合作价值：场景化内容定制 + 品效指标闭环，覆盖购车决策到生活表达',
      ],
    },
  },
  {
    name: '2026巨量星图「潜力宝藏达人团」',
    statusLabel: 'NEW',
    docUrl:
      'https://bytedance.larkoffice.com/wiki/VLNBwKSyRioS6gkulvxca0ORn9g?from=from_copylink',
    coverImage: potentialTeamHero,
    coverAlt:
      '2026巨量星图「潜力宝藏达人团」飞书文档头图：潜力宝藏达人团主视觉',
    docSummary: {
      subtitle: '已发布资料：项目总览',
      bullets: [
        '营销周期：Y26-Q4',
        '营销方向：口碑种草 / 节庆种草 / 选购转化 / 复购转化',
        '合作方式：星图直充合作，最低合作金额 20 万起（文档原文）',
      ],
    },
  },
  {
    name: '2026巨量星图「新年焕新达人团」',
    statusLabel: 'NEW',
    docUrl: 'https://bytedance.larkoffice.com/wiki/YWIBw2B1PiujDFkjE7mc3gIgnYf',
    coverImage: newYearTeamHero,
    coverAlt:
      '2026巨量星图「新年焕新达人团」飞书文档封面图：新年焕新达人团主视觉',
    docSummary: {
      subtitle: '已发布资料：项目总览',
      bullets: [
        '营销节点：2026年12月–2027年2月（双旦 & CNY）',
        '六大方向：家庭焕新 / 悦己焕新 / 礼赠焕新 / 专业测评 / 生活实测 / 采购清单',
        '合作链路：创造需求 → 辅助决策 → 承接购买',
      ],
    },
  },
  { name: '2026巨量星图「优质参数研究院」', statusLabel: '敬请期待' },
  { name: '2026巨量星图达人团【真实家庭实验】', statusLabel: '敬请期待' },
  { name: '2026巨量星图「种收有道·短直达人团」', statusLabel: '敬请期待' },
  { name: '2026巨量星图「旅行科普」达人团', statusLabel: '敬请期待' },
  { name: '目2026巨量星图服饰行业「创意营销」达人团', statusLabel: '敬请期待' },
  {
    name: '2026巨量星图服饰行业「婴童权威种草」达人团',
    statusLabel: '敬请期待',
  },
  { name: '2026巨量星图美妆行业「优质成分研究院」', statusLabel: '敬请期待' },
  {
    name: '2026巨量星图母婴行业「教育行业达人团」达人团',
    statusLabel: '敬请期待',
  },
];

export function TeamModule() {
  return (
    <section id="module-content" className="content-section enter team-module">
      <div className="section-heading">
        <div>
          <span className="eyebrow">MODULE · 04</span>
          <h2>达人团供给</h2>
          <p>
            共 13 个达人团，已上线资料的达人团标注
            NEW，并提供文档入口；其余保持「敬请期待」状态。
          </p>
        </div>
      </div>

      <div className="team-grid">
        {TEAMS.map(team => (
          <article key={team.name} className="team-card">
            <header className="team-card-head">
              <div className="team-card-title">
                <UsersRound size={18} />
                <strong>{team.name}</strong>
              </div>
              <span
                className={
                  team.statusLabel === 'NEW'
                    ? 'team-status team-status-new'
                    : 'team-status'
                }
              >
                {team.statusLabel}
              </span>
            </header>

            <figure
              className={
                team.coverImage ? 'team-cover' : 'team-cover team-cover-empty'
              }
            >
              {team.coverImage ? (
                <img src={team.coverImage} alt={team.coverAlt ?? team.name} />
              ) : (
                <div className="team-cover-placeholder">资料整理中</div>
              )}
            </figure>

            {team.docSummary ? (
              <div className="team-doc">
                <div className="team-doc-title">
                  <BookOpen size={14} />
                  <span>{team.docSummary.subtitle}</span>
                </div>
                <ul>
                  {team.docSummary.bullets.map(item => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="team-desc">待上线……</p>
            )}

            {team.docUrl ? (
              <a
                className="team-link"
                href={team.docUrl}
                target="_blank"
                rel="noreferrer"
              >
                查看文档 <ArrowUpRight size={14} />
              </a>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
