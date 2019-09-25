import WilcoxonPlotTile from './WilcoxonPlotTile.vue';
import AnovaTableTile from './AnovaTableTile.vue';
import HeatmapTile from './HeatmapTile.vue';
import { plot_types } from '../../utils/constants';

export default [
  {
    path: 'wilcoxon',
    name: 'Wilcoxon test',
    shortName: 'Wilcoxon Test',
    description: 'TODO R custom code',
    component: WilcoxonPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
  },
  {
    path: 'anova',
    name: 'ANOVA',
    shortName: 'ANOVA',
    description: 'TODO R custom code',
    component: AnovaTableTile,
    args: {},
    type: plot_types.ANALYSIS,
  },
  {
    path: 'heatmap',
    name: 'Heatmap',
    shortName: 'Heatmap',
    description: 'cool stuff',
    component: HeatmapTile,
    args: {},
    type: plot_types.ANALYSIS,
  },
];
