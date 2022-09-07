library(data.table)
library(ggplot2)
library(igraph)
library(purrr)
library(cowplot)
library(tm) 
library(wordcloud)


setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# Read processed data

# all treaties and variables
bits_full <- fread("full_cleaned_iia.csv")
# only bilateral investment treaties for map
bits <- fread("lat_lon_bits.csv")

# Nodes are the distinct set of signer countries and their capital city coordinates
nodes <- unique(rbind(bits[,.(signer_1, 
        CapitalLatitude_signer_1, CapitalLongitude_signer_1)],
bits[,.(signer_2, 
        CapitalLatitude_signer_2, CapitalLongitude_signer_2)], use.names=FALSE))

# Create year-related variables
bits[,"year_wt":= (((floor(year / 10) * 10)-1900)*0.001)^0.5]
bits$decade <- (floor(bits$year / 10) * 10)

# Turn full dataset into a graph 
g <- graph_from_data_frame(bits[,.(signer_1, signer_2, year, year_wt,
                                   CapitalLatitude_signer_1, CapitalLongitude_signer_1,
                                   CapitalLatitude_signer_2, CapitalLongitude_signer_2)], 
                           directed = FALSE,
                           vertices = nodes)

# Give the nodes (countries) weights 
nodes$weight = degree(g)

# Define a map ggplot theme
maptheme <- theme(panel.grid = element_blank()) +
  theme(axis.text = element_blank()) +
  theme(axis.ticks = element_blank()) +
  theme(axis.title = element_blank()) +
  theme(legend.position = "bottom") +
  theme(legend.justification = "center") +
  theme(legend.key=element_blank()) +
  theme(panel.grid = element_blank()) +
  theme(panel.background = element_rect(fill = "#FFFFFF")) +
  theme(plot.margin = unit(c(0, 0, 0.5, 0), 'cm'))

# Use preloaded worldmap data to plot country shapes
country_shapes <- geom_polygon(aes(x = long, y = lat, group = group),
                               data = map_data('world'),
                               fill = "#c8c8c8", color = "#515151",
                               size = 0.15)
# set coordinate limits
mapcoords <- coord_fixed(xlim = c(-150, 180), ylim = c(-55, 80))

# Define colors
cols00 <- c("#328f7f", "red", 
            "#328f7f", "#328f7f", "#328f7f", "#328f7f", "#328f7f")
cols10 <- c("#a51417", "#328f7f", 
            "#328f7f", "#328f7f", "#328f7f", "#328f7f", "#328f7f")
cols90 <- c("#328f7f", "#328f7f", 
            "red", "#328f7f", "#328f7f", "#328f7f", "#328f7f")
decades <- c("2010" , "2000" , "1990", "1980" , "1970" ,
             "1960","1950")

# Make mapped network plots
bits2010 <- ggplot() + country_shapes +
  geom_curve(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, xend = CapitalLongitude_signer_2, 
                 yend = CapitalLatitude_signer_2, colour = factor(bits$decade),size=bits$year_wt),
             data = bits, curvature = 0.5,
             alpha = 0.2, inherit.aes = TRUE, show.legend = TRUE) +
  scale_size_continuous(guide = "none", range = c(0.25, 2)) + 
  scale_colour_manual(name = "Decade:", values = setNames(cols10, unique(bits$decade)), 
                                         labels = setNames(decades, unique(bits$decade)))+
  guides(colour = guide_legend(nrow = 1))+
  geom_point(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, size = weight),         
             data = nodes,
             shape = 21, color="#6c7373",
             fill = '#faa200', stroke = 0.5) + 
  mapcoords + maptheme  

ggsave(
  "plots/bit_map.png",
  plot = bits2010,
  width = 825,
  height = 366,
  units = "px",
  bg = "#FFFFFF"
)


bits2000 <- ggplot() + country_shapes +
  geom_curve(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, xend = CapitalLongitude_signer_2, 
                 yend = CapitalLatitude_signer_2, colour = factor(bits$decade),size=bits$year_wt),
             data = bits, curvature = 0.4,
             alpha = 0.2, inherit.aes = TRUE, show.legend = TRUE) +
  scale_size_continuous(guide = "none", range = c(0.25, 2)) + 
  scale_colour_manual(name = "Decade", values = setNames(cols00, unique(bits$decade)), 
                      labels = setNames(decades, unique(bits$decade)))+
  geom_point(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, size = weight),          
             data = nodes,
             shape = 21, color="#6c7373",
             fill = '#faa200', stroke = 0.5) + 
  mapcoords + maptheme

bits1990 <- ggplot() + country_shapes +
  geom_curve(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, xend = CapitalLongitude_signer_2, 
                 yend = CapitalLatitude_signer_2, colour = factor(bits$decade),size=bits$year_wt),
             data = bits, curvature = 0.4,
             alpha = 0.2, inherit.aes = TRUE, show.legend = FALSE) +
  scale_size_continuous(guide = "none", range = c(0.25, 2)) + 
  scale_colour_manual(name = "decades", values = setNames(cols90, unique(bits$decade)), 
                      labels = setNames(decades, unique(bits$decade)))+
  geom_point(aes(x = CapitalLongitude_signer_1, y = CapitalLatitude_signer_1, size = weight),           # draw nodes
             data = nodes,
             shape = 21, color="#6c7373",
             fill = '#faa200', stroke = 0.5) + 
  mapcoords + maptheme



# Density plot showing gdp pc delta distributions per treaty group
gdp<-ggplot()+
  geom_density(aes(x=gdp_delta, fill="Host Country Interests"), data=bits_full[interest_dummy==1,], alpha=0.5, size=0.1)+
  geom_density(aes(x=gdp_delta, fill="Not Mentioned"), data=bits_full[interest_dummy==0,], alpha=0.5, size=0.1)+
  labs(x="GDP PC Delta", y="Density\n") +
  scale_fill_manual(name="Treaty Type", 
                    labels=c("Host Country Interests", "Not Mentioned"), 
                    values = c("Host Country Interests" = "#328f7f", 
                               "Not Mentioned" = "#6c7373"))+
 geom_vline(xintercept = mean(bits_full[interest_dummy==0,gdp_delta], na.rm = TRUE), color="#6c7373", 
             size=0.5, linetype="dashed")+
  geom_vline(xintercept = mean(bits_full[interest_dummy==1,gdp_delta], na.rm = TRUE), color="#328f7f", 
             size=0.5, linetype="dashed")+
  theme_minimal()

# Density plot showing polity 5 delta distributions per treaty group
polity <- ggplot()+
  geom_density(aes(x=polity2_delta, fill="Host Country Interests"), data=bits_full[interest_dummy==1,], alpha=0.5, size=0.1)+
  geom_density(aes(x=polity2_delta, fill="Not Mentioned"), data=bits_full[interest_dummy==0,], alpha=0.5, size=0.1)+
  labs(x="Polity 5 Delta", y="Density\n") +
  scale_fill_manual(name="Treaty Type", 
                    labels=c("Host Country Interests", "Not Mentioned"), 
                    values = c("Host Country Interests" = "#328f7f", 
                               "Not Mentioned" = "#6c7373"))+
  geom_vline(xintercept = mean(bits_full[interest_dummy==0,polity2_delta], na.rm = TRUE), color="#6c7373", 
             size=0.5, linetype="dashed")+
  geom_vline(xintercept = mean(bits_full[interest_dummy==1,polity2_delta], na.rm = TRUE), color="#328f7f", 
             size=0.5, linetype="dashed")+
  theme_minimal()


# Density plot showing agricultural exports share delta distributions per treaty group
agexp <- ggplot()+
  geom_density(aes(x=agexp_delta, fill="Host Country Interests"), data=bits_full[interest_dummy==1,], alpha=0.5, size=0.1, show.legend = F)+
  geom_density(aes(x=agexp_delta, fill="Not Mentioned"), data=bits_full[interest_dummy==0,], alpha=0.5, size=0.1, show.legend = F)+
  labs(x="Agricultural Exports Delta", y="Density\n") +
  scale_fill_manual(name="Treaty Type", 
                    labels=c("Host Country Interests", "Not Mentioned"), 
                    values = c("Host Country Interests" = "#328f7f", 
                               "Not Mentioned" = "#6c7373"))+
  geom_vline(xintercept = mean(bits_full[interest_dummy==0,agexp_delta], na.rm = TRUE), color="#6c7373", 
             size=0.5, linetype="dashed")+
  geom_vline(xintercept = mean(bits_full[interest_dummy==1,agexp_delta], na.rm = TRUE), color="#328f7f", 
             size=0.5, linetype="dashed")+
  theme_minimal()

# Plot agricultural export share and gdp pc deltas together
density_combo <- plot_grid(agexp,gdp)


ggsave(
  "plots/dens_combo.png",
  plot = density_combo,
  scale = 1,
  width = 825,
  height = 366,
  units = "px",
  bg = "#FFFFFF"
)


# Histograms as alternatives to the density plots
gdppc_hist <- ggplot()+
  geom_histogram(aes(x=gdp_delta, fill="Not Mentioned"), data=bits_full[interest_dummy==0,], alpha=0.3, bins = 80)+
  geom_histogram(aes(x=gdp_delta, fill="Mentioned"), data=bits_full[interest_dummy==1,], alpha=0.5, bins = 80)+
  labs(x="GDP PC Delta", y="Number of Treaties\n") +
 geom_vline(xintercept = mean(bits_full[interest_dummy==0,gdp_delta], na.rm = TRUE), color="#a51417", 
             size=0.5, linetype="dashed")+
  geom_vline(xintercept = mean(bits_full[interest_dummy==1,gdp_delta], na.rm = TRUE), color="#328f7f", 
             size=0.5, linetype="dashed")+
  scale_fill_manual(name="Host Country Interests", labels=c("Mentioned", "Not Mentioned"), values = c("Host Country Interests" = "#328f7f",
                                                                                                        "Not Mentioned" = "#a51417"))+
  theme_minimal()


polity_hist <- ggplot()+
  geom_histogram(aes(x=polity2_delta, fill="Not Mentioned"), data=bits_full[interest_dummy==0,], alpha=0.3, bins=10)+
  geom_histogram(aes(x=polity2_delta, fill="Mentioned"), data=bits_full[interest_dummy==1,], alpha=0.5, bins=10)+
  labs(x="Polity 5 Delta", y="Number of Treaties\n") +
  geom_vline(xintercept = mean(bits_full[interest_dummy==0,polity2_delta], na.rm = TRUE), color="#a51417", 
             size=0.5, linetype="dashed")+
  geom_vline(xintercept = mean(bits_full[interest_dummy==1,polity2_delta], na.rm = TRUE), color="#328f7f", 
             size=0.5, linetype="dashed")+
  scale_fill_manual(name="Host Country Interests", labels=c("Mentioned", "Not Mentioned"), values = c("Host Country Interests" = "#328f7f",
                                                                                                        "Not Mentioned" = "#a51417"))+
  theme_minimal()

# Make time series of treaties per year
ts_bit <- bits_full[,.N, by=.(year)]

# Make "long" version of the interst outcomes
wide_int_type <- melt(bits_full[,.N, by=.(year, economic,governance, general, environmental)]
, id.vars = c("year"),
     measure.vars = c("economic", "governance", "environmental","general"))

# Merge with time series
dat <- merge.data.table(wide_int_type, ts_bit, by="year")

# Make the year a date for plotting purposes
dat[,"year" := lubridate::as_date(paste("12-31-",year), format="%m-%d-%Y")]

treaty_counts <- ggplot(data=dat, aes(x=year, y=value, fill=factor(dat$variable))) +
  geom_col(alpha=0.7) +
  geom_line(aes(x=year, y=N, color = "#6c7373"), linetype="longdash", alpha=0.7)+
  scale_color_manual(name = "Total Treaties Signed", values = setNames(c("#6c7373"), 0), 
                    labels = setNames(c(""), 0))+theme_minimal()+
  scale_x_date(date_breaks = "5 year", date_labels = "%Y", expand=c(0,0))+ 
  scale_fill_manual(name = "Interest Type", values = setNames(c("#c8c8c8","#faa200","#328f7f","#a51417"), unique(dat$variable)), 
                      labels = setNames(c("Economic", "Governance","Environmental", "General"), unique(dat$variable)))+theme_minimal()+
  labs(x="\nYear",y="Number of Treaties\n")

ggsave(
  "plots/interest_type_bar.png",
  plot = treaty_counts,
  scale = 1,
  width = 825,
  height = 366,
  units = "px",
  bg = "#FFFFFF"
)

# wide_treaty_type <- bits_full[,.N, .(is_BIT, is_AA, is_EPA, is_FTA, is_MIT, is_OTHER)]
# 
# wide_treaty_type <- melt(wide_treaty_type
#                       , id.vars = c("V1"),
#                       measure.vars = c("is_BIT", "is_AA", "is_EPA", "is_FTA", "is_MIT", "is_OTHER"))
# 
# 
# wide_treaty_type <- wide_treaty_type[value==1]
# 
# treaty_types <- ggplot(wide_treaty_type, aes(x=reorder(variable, -V1), y=V1))+
#   geom_col(fill="#a51417") + labs(x="Treaty Type", y="Total Count") + theme_minimal()
# 
# ggsave(
#   "plots/treaty_type_bar.png",
#   plot = treaty_types,
#   scale = 1,
#   width = 825,
#   height = 366,
#   units = "px",
#   bg = "#FFFFFF"
# )

# Read in processed text string
a <-scan("./int_treaties.txt", what = "character")
a <- VCorpus(VectorSource(a))

# Generate Word Cloud
dev.off()
png("plots/wc.png")
wordcloud(a, 
          min.freq = 10,
          scale=c(3,0.2),
          max.words = 200, 
          random.order = TRUE, 
          random.color = FALSE,
          colors=c("#c8c8c8","#faa200","#328f7f","#a51417"))
dev.off()



# 825 x 366
