const width = 700;
const height = 500;
const slider_length = 300;
const slider_month_length = 350;
const slider_year_left = 200;
const slider_month_left = 20;

const geoJSONPath = "../HeatMap/data/china.json";
const dataPath = "../HeatMap/data/datas.csv";

const minYear = 2013;
const maxYear = 2018;
const years = [2013, 2014, 2015, 2016, 2017, 2018]
const months = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
let nowYear = 2013;
let nowMonth = 12;

const qualities = ["优", "良", "轻度污染", "中度污染", "重度污染", "严重污染"]

const province_aqi_map = {}
let geojson = []
let datas = []

const svg = d3.select("#heat_map")
    .attr("width", width)
    .attr("height", height);

svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'none')
    .attr('stroke', 'grey');

// 传递省份数据
function clickProvince(province) {
    //TODO:将数据传给其他图，可传递以下三个数据
    console.log(province);
    console.log(nowYear);
    console.log(nowMonth);
}

// 更新AQI_MAP
function updateAQIMap(data) {
    for(let i = 0; i < data.length; i++) {
        province_aqi_map[data[i]["province"]] = data[i]["AQI"];
    }
}

// 年份和月份变更后更新数据
function updateData(rawData) {
    let newData = rawData.filter(d => parseInt(d["year"]) === nowYear && parseInt(d["month"]) === nowMonth);
    updateAQIMap(newData);
}

// 颜色计算器
function colorComputerByAQI(data) {
    let linear0 = d3.scaleLinear()
        .domain([0, 50]).range([0, 1]);
    let linear1 = d3.scaleLinear()
        .domain([51, 100]).range([0, 1]);
    let linear2 = d3.scaleLinear()
        .domain([101, 150]).range([0, 1]);
    let linear3 = d3.scaleLinear()
        .domain([151, 200]).range([0, 1]);
    let linear4 = d3.scaleLinear()
        .domain([201, 300]).range([0, 1]);
    let linear5 = d3.scaleLinear()
        .domain([301, 500]).range([0, 1]);
    let colorComputer0 = d3.interpolate("rgb(2,96,2)", "rgb(122,198,3)");
    let colorComputer1 = d3.interpolate("rgb(254, 252, 11)", "rgb(250, 156, 5)");
    let colorComputer2 = d3.interpolate("rgb(193,121,6)", "rgb(225,44,16)");
    let colorComputer3 = d3.interpolate("rgb(225,44,16)", "rgb(96,22,0)");
    let colorComputer4 = d3.interpolate("rgb(96,22,0)", "rgb(59, 13, 0)");
    let colorComputer5 = d3.interpolate("rgb(59, 13, 0)", "rgb(0, 0, 0)");


    if (data <= 50) {
        return colorComputer0(linear0(data));
    } else if (data <= 100) {
        return colorComputer1(linear1(data));
    } else if (data <= 150) {
        return colorComputer2(linear2(data));
    }  else if (data <= 200) {
        return colorComputer3(linear3(data));
    } else if (data <= 300){
        return colorComputer4(linear4(data));
    } else {
        return colorComputer5(linear5(data));
    }
}

// 处理年份月份变更事件
function processChange() {
    updateData(datas);
    svg.selectAll(".china")
        .transition()
        .attr("fill", function(d) {
            return colorComputerByAQI(parseFloat(province_aqi_map[d["properties"]["name"]]));
        });
}

// 添加年份切换滑动条
function addSlider() {
    let year_slider = d3.select("body")
        .append('g')
        .attr("id", "slider");
    year_slider.append('input')
        .attr("type", "range")
        .attr("min", minYear)
        .attr("max", maxYear)
        .attr("step", 1)
        .attr("id", "slider_input")
        .style("position", "absolute")
        .style("top", height - 50 + "px")
        .style("left", slider_year_left + "px")
        .style("width", slider_length + "px")
        .on("mousemove", function(d, i) {
            if(parseInt(this.value) !== nowYear) {
                nowYear = parseInt(this.value);
                processChange();
            }
        });

    year_slider.append('g')
        .selectAll("span")
        .data(years)
        .enter()
        .append('span')
        .text(d => d)
        .style('position', "absolute")
        .style("top", height - 30 + "px")
        .style("left", (d, i) => {
            return i * (slider_length / (years.length - 1)) + slider_year_left - 10 + "px";
        });

    let month_slider = d3.select("body")
        .append('g')
        .attr("id", "month_slider");

    month_slider.append('input')
        .attr("type", "range")
        .attr("min", 1)
        .attr("max", 12)
        .attr("step", 1)
        .attr("id", "slider_input_month")
        .style("position", "absolute")
        .style("top", height / 2 - 150 + "px")
        .style("left", slider_month_left + "px")
        .style("width", "40px")
        .style("height", slider_month_length + "px")
        .on("mousemove", function(d, i) {
            if(parseInt(this.value) !== nowMonth) {
                nowMonth = parseInt(this.value);
                processChange();
            }
        });

    month_slider.append('g')
        .selectAll("span")
        .data(months)
        .enter()
        .append('span')
        .text(d => (d + "月"))
        .style('position', "absolute")
        .style("top", (d, i) => {
            return i * (slider_month_length / (months.length - 1)) + 95 + "px";})
        .style("left", slider_month_left + 40 + "px");
}

// 添加名称数据显示框
function addToolTip() {
    let tooltip = d3.select("body")
        .append('div')
        .attr("id", "tooltip")
        .attr("class", "hidden")
    tooltip.append('p')
        .append('span')
        .attr("id", "province_name")
        .text("name");
    tooltip.append('p')
        .append('span')
        .text("AQI 指数：")
        .append('span')
        .attr("id", "aqi_value")
    tooltip.append('p')
        .append('span')
        .text("空气质量：")
        .append('span')
        .attr("id", "quality");
}

function drawHeatMap() {
    Promise.all([
        d3.json(geoJSONPath),
        d3.csv(dataPath)
    ]).then((data) => {
        geojson = data[0];
        datas = data[1];
        updateData(datas);
        const projection = d3.geoMercator()
            .center([463, 36])
            .scale(500)
            .translate([width / 2, height / 2]);
        const path = d3.geoPath().projection(projection);
        const features = geojson["features"];

        svg.append('g')
            .attr('class', 'map')
            .selectAll('.china')
            .data(features)
            .join('path')
            .attr('class', 'china')
            .attr("fill", function(d, i) {
                return colorComputerByAQI(parseFloat(province_aqi_map[d["properties"]["name"]]));
            })
            .attr('d', path)
            .on("mouseover", function(d, i) {
                let province = d["properties"]["name"];
                let aqi = province_aqi_map[province];
                let xPosition = projection(d["properties"]["center"])[0]
                let yPosition = projection(d["properties"]["center"])[1]
                let tooltip = d3.select("#tooltip")
                    .style("left", xPosition + "px")
                    .style("top", yPosition - 40 + "px");
                tooltip.classed("hidden", false);
                tooltip.select("#province_name")
                    .text(province);
                tooltip.select("#aqi_value")
                    .text(parseFloat(aqi).toFixed(2));
                let quality = qualities[0]
                let aqi_value = parseFloat(aqi);
                if(aqi_value <= 50) {
                    quality = qualities[0];
                } else if (aqi_value <= 100) {
                    quality = qualities[1];
                } else if (aqi_value <= 150) {
                    quality = qualities[2];
                } else if (aqi_value <= 200) {
                    quality = qualities[3];
                } else if (aqi_value <= 300) {
                    quality = qualities[4];
                } else {
                    quality = qualities[5];
                }
                tooltip.select("#quality")
                    .text(quality);
                d3.selectAll('.china')
                    .attr("opacity", 0.7);
                d3.select(this)
                    .attr("opacity", 1.3);
            })
            .on("mouseout", function(d, i) {
                d3.select("#tooltip").classed("hidden", true);
                d3.selectAll('.china')
                    .attr("opacity", 1.0);
            })
            .on("click", function(d) {
                let province = d["properties"]["name"];
                clickProvince(province);
            });
    });
}

drawHeatMap();
addSlider();
addToolTip();