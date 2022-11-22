<template>
  <div class="leaves">
    <span></span><br />
    <span>🌧🌧🌧</span><br />
    <span>夏天结束了</span><br />
    <span>转眼又到了冬天</span><br />
    <span>期末考试不出所料成绩一塌糊涂</span><br />
    <span>浪费了好几张昂贵的皮革</span><br />
    <span>寒假仍然每天打工</span><br />
    <span>每当外出时又要多加一件衣服</span><br />
    <span>总想到 那个人</span><br />
    <span>她还好吗</span><br />
    <span>...</span><br />
    <span>回望当初</span><br />
    <span>那时我也一定一直在</span><br />
    <span>训练自己迈步</span><br />
    <span>如果有一天</span><br />
    <span>能够走得更稳更远了</span><br />
    <span>就去见她吧</span><br />
    <span>🌨🌨🌨</span><br />
  </div>
  <div class="flower">
    {{ day }} ❀ {{ fix(hour) }}:{{ fix(minute) }}:{{ fix(seccond) }}
  </div>
</template>

<script>
export default {
  data() {
    return {
      start: new Date("2022/02/20 19:30:00").getTime(),
      day: 0,
      hour: 0,
      minute: 0,
      seccond: 0,
      interval: null,
    };
  },
  methods: {
    timediff() {
      let self = this;
      let now = new Date().getTime(),
        leave = Math.floor((now - self.start) / 1000);
      self.day = Math.floor(leave / 86400);
      leave = leave % 86400;
      self.hour = Math.floor(leave / 3600);
      leave = leave % 3600;
      self.minute = Math.floor(leave / 60);
      leave = leave % 60;
      self.seccond = leave;
      self.show = true;
    },
    fix(val) {
      return (Array(2).join(0) + val).slice(-2);
    },
  },

  mounted() {
    let self = this;
    self.timediff();
    this.interval = setInterval(() => {
      self.timediff();
    }, 500);
  },
  unmounted: function () {
    clearInterval(this.interval);
  },
};
</script>

<style scoped>
.leaves {
  display: inline-block;
  /* background: linear-gradient(150deg, #7ee641, #042502); */
  background: linear-gradient(150deg, #042502, #7ee641); 
  -webkit-background-clip: text;
  color: transparent;
}

.flower {
  padding-top: 10px;
  font-family: "Comic Sans MS", Arial, Helvetica, cursive, sans-serif;
  color: #f67cd3;
}
</style>