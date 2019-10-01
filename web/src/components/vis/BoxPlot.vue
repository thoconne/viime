<script>
import { select } from 'd3-selection';
import { scaleBand } from 'd3-scale';
import { boxplot, boxplotStats } from 'd3-boxplot';
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';
import { measurementColumnName, measurementValueName } from '../../utils/constants';


export default {
  mixins: [
    axisPlot,
  ],
  props: {
    width: {
      type: Number,
      default: 400,
    },
    height: {
      type: Number,
      default: 300,
    },
    rows: { // {name: string, values: number[]}[]
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      margin: {
        top: 20,
        right: 20,
        bottom: 50,
        left: 120,
      },
      duration: 200,
      ylabel: measurementColumnName,
      xlabel: measurementValueName,
      refsMounted: false,
    };
  },
  computed: {
    reactiveUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.update();
      return '';
    },
    scaleY() {
      const { rows, dheight } = this;
      return scaleBand()
        .domain(rows.map(d => d.name))
        .range([0, dheight], 0.1);
    },
    xrange() {
      let min = Number.POSITIVE_INFINITY;
      let max = Number.NEGATIVE_INFINITY;
      this.rows.forEach((row) => {
        row.values.forEach((v) => {
          if (v < min) {
            min = v;
          }
          if (v > max) {
            max = v;
          }
        });
      });
      return [min, max];
    },
  },

  mounted() {
    this.refsMounted = true;
  },

  methods: {
    update() {
      if (!this.$refs.svg) {
        return;
      }
      //
      // Compute the total variance in all the PCs.
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);

      // Draw the data.

      const layout = boxplot()
        .scale(this.scaleX)
        .vertical(false)
        .bandwidth(this.scaleY.bandwidth())
        .boxwidth(this.scaleY.bandwidth() * 0.8)
        .showInnerDots(false);

      const stats = this.rows.map(d => Object.assign({}, d, boxplotStats(d.values)));
      const boxplots = svg.select('.plot').selectAll('g.boxplot').data(stats)
        .join(enter => enter.append('g').classed('boxplot', true))
        .attr('transform', d => `translate(0, ${this.scaleY(d.name)})`);

      // update
      const finished = boxplots
        .transition()
        .duration(this.duration)
        .call(layout)
        .end();

      finished.then(() => {
        // inject tooltips

        const f = d => d.toFixed(3);

        // outliers: show the value
        boxplots.select('g.point').selectAll('.outlier').html(d => `<title>${f(d.value)}</title>`);

        const count = (values, min, max) => values
          .reduce((acc, v) => acc + (v >= min && v < max ? 1 : 0), 0);

        // inject rect backgrounds for whiskers
        const base = boxplots.select('.whisker');

        boxplots.select('.whisker path')
          .html(d => `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`);
        boxplots.select('.box line')
          .html(d => `<title>${d.name}: ${f(d.fiveNums[1])} (q1) - ${f(d.fiveNums[2])} (median) = ${count(d.values, d.fiveNums[1], d.fiveNums[2])} Items</title>`);
        boxplots.select('.box line:last-of-type')
          .html(d => `<title>${d.name}: ${f(d.fiveNums[2])} (median) - ${f(d.fiveNums[3])} (q3) = ${count(d.values, d.fiveNums[2], d.fiveNums[3])} Items</title>`);
        boxplots.select('.whisker path:last-of-type')
          .html(d => `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`);

        const bandwidth = this.scaleY.bandwidth();
        const bgs = base.selectAll('rect').data(d => [d, d]).join('rect');
        bgs
          .attr('x', (d, i) => this.scaleX(Math.min(d.whiskers[i].start, d.whiskers[i].end)))
          .attr('y', bandwidth * -0.5)
          .attr('width', (d, i) => this.scaleX(Math.abs(d.whiskers[i].start - d.whiskers[i].end)))
          .attr('height', bandwidth)
          .style('fill', 'transparent')
          .html((d, i) => (i === 0
            ? `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`
            : `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`));
      });
    },
  },
};
</script>

<template lang="pug">
svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg",
    :data-update="reactiveUpdate")
  g.master
    g.axes
    g.plot
  text.x.label(:transform="`translate(${margin.left + dwidth / 2},${height - 10})`")
    | {{xlabel}}
  text.y.label(:transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`")
    | {{ylabel}}
</template>

<style scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}
</style>