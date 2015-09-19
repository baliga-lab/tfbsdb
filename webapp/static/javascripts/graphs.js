var nwpgraphs;
if (!nwpgraphs) {
    nwpgraphs = {};
}

(function () {
     "use strict";
     nwpgraphs.histogram = function(selector, histData) {
         var values = histData.values;
         // A formatter for counts.
         var formatCount = d3.format(",.0f");
         var margin = {top: 10, right: 10, bottom: 30, left: 30},
         width = 500 - margin.left - margin.right,
         height = 200 - margin.top - margin.bottom;

         // Generate a histogram using twenty uniformly-spaced bins.
         var data = d3.layout.histogram().bins(35)(values).reverse();
         var x = d3.scale.linear()
             .domain([d3.max(data, function(d) { return d.x; }),
                      d3.min(data, function(d) { return d.x; })])
             .range([0, width]);
         var y = d3.scale.linear()
             .domain([0, d3.max(data, function(d) { return d.y; })])
             .range([height, 0]);

         var barWidth = data.length >= 2 ? x(data[1].x) - x(data[0].x) : 5;
         var xAxis = d3.svg.axis()
             .scale(x)
             .orient("bottom");
         var yAxis = d3.svg.axis()
             .scale(y)
             .orient("left");

         var svg = d3.select(selector).append("svg")
             .attr('class', 'chart')
             .attr("width", width + margin.left + margin.right)
             .attr("height", height + margin.top + margin.bottom)
           .append("g")
             .attr("transform", "translate(" + margin.left + "," +
                   margin.top + ")");

         svg.selectAll('rect').data(data)
           .enter().append('rect')
           .attr("x", function(d) { return x(d.x); })
           .attr("y", function(d) { return y(d.y); })
           .attr('width', function(d) { return barWidth; })
           .attr('height', function(d) { return height - y(d.y); });

         svg.append("g")
             .attr("class", "x axis")
             .attr("transform", "translate(0, " + height + ")")
             .call(xAxis);

         svg.append("text")      // text label for the x axis
             .attr("x", width / 2 )
             .attr("y",  height + margin.bottom)
             .style("text-anchor", "middle")
             .text("Position Relative to TSS (bp)");

         svg.append("g")
             .attr("class", "y axis")
             .call(yAxis);

         svg.append("text")
             .attr("transform", "rotate(-90)")
             .attr("y", -10 - margin.left)
             .attr("x",0 - (height / 2))
             .attr("dy", "1em")
             .style("text-anchor", "middle")
             .text("Frequency");
        
         

     };
}());
